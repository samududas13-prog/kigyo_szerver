import argparse
import asyncio
import json
from typing import Dict, Optional
import websockets
import os
from kozos_jatekmag import Beallitasok, SzinSeged, VilagAllapot
import time
import random

class KapcsolatAdat:
    def __init__(self, websocket):
        self.websocket = websocket  
        self.azonosito = ""
        self.szoba_kod = ""
        self.nev = ""
        self.szin = (200, 200, 200)
        self.szelesseg = 1400
        self.magassag = 830
        self.ip_cim = ""
        self.csatlakozott = False
        self.nagy_csomag_kuldes = 0


class SzobaAdat:
    def __init__(self, kod: str, jatek_mode, nehezseg_szint, beallitasok: Beallitasok):
        self.kapcsolat_adatcsomag_szetosztas_szamolas = 0
        self.kuldes_szamolo = 0
        self.kod = kod  
        self.jatek_mode = jatek_mode
        self.nehezseg_szint = nehezseg_szint
        self.beallitasok = beallitasok
        self.vilag = VilagAllapot(beallitasok, jatek_mode, nehezseg_szint) 
        self.kapcsolatok: Dict[str, KapcsolatAdat] = {} 
        self.fut = True 
        self.kovetkezo_azonosito = 1
        self.jatek_task: Optional[asyncio.Task] = None
        self.elozo_ido = time.perf_counter()
        
    def uj_azonosito(self):
        azonosito = f"jatekos_{self.kovetkezo_azonosito}"
        self.kovetkezo_azonosito += 1
        return azonosito

    async def jatek_loop(self):
        while self.fut:
            await asyncio.sleep(1 / self.beallitasok.szerver_fps)

            most = time.perf_counter()
            delta_ido = most - self.elozo_ido
            self.elozo_ido = most
            delta_ido = min(delta_ido, 0.05)

            self.vilag.frissites(delta_ido)

            self.kuldes_szamolo += 1
            if self.kuldes_szamolo >= self.beallitasok.szerver_kliens_szabályuzott_kuldes:
                self.kuldes_szamolo = 0

            bontando_azonositok = []

            for azonosito, kapcsolat in list(self.kapcsolatok.items()):
                if not kapcsolat.csatlakozott:
                    continue

                if self.kuldes_szamolo == kapcsolat.nagy_csomag_kuldes:
                    allapot = self.vilag.nezet_jatekosnak(azonosito, kapcsolat.szelesseg, kapcsolat.magassag)
                else:
                    allapot = self.vilag.nezet_jatekosnak_kicsi(azonosito, kapcsolat.szelesseg, kapcsolat.magassag)

                uzenet = json.dumps({"tipus": "allapot", "allapot": allapot})

                try:
                    await kapcsolat.websocket.send(uzenet)
                except Exception:
                    bontando_azonositok.append(azonosito)

            for azonosito in bontando_azonositok:
                await self.jatekos_torlese(azonosito)

            if not self.kapcsolatok:
                self.fut = False
                break

    async def jatekos_hozzaadasa(self, kapcsolat: KapcsolatAdat, kep):
        kapcsolat.azonosito = self.uj_azonosito()
        kapcsolat.szoba_kod = self.kod
        kapcsolat.csatlakozott = True
        kapcsolat.nagy_csomag_kuldes = self.kapcsolat_adatcsomag_szetosztas_szamolas
        self.kapcsolat_adatcsomag_szetosztas_szamolas += 1
        if self.kapcsolat_adatcsomag_szetosztas_szamolas >= self.beallitasok.szerver_kliens_szabályuzott_kuldes:
            self.kapcsolat_adatcsomag_szetosztas_szamolas = 0
        self.kapcsolatok[kapcsolat.azonosito] = kapcsolat
        kep = kep
        self.vilag.jatekos_hozzaadasa(kapcsolat.azonosito, kapcsolat.nev, kapcsolat.szin, kep)
        return kapcsolat.azonosito

    async def jatekos_torlese(self, azonosito):
        kapcsolat = self.kapcsolatok.pop(azonosito, None)
        self.vilag.jatekos_torlese(azonosito)
        if kapcsolat is not None:
            try:
                await kapcsolat.websocket.close()
            except Exception:
                pass


class KozpontiSzerver:
    def __init__(self, host, port):
        self.host = host  
        self.port = port
        self.beallitasok = Beallitasok()
        self.szobak = {}

    def _veletlen_kod(self):
        for _ in range(100000):
            kod = f"{self.beallitasok.rng.randint(0, 99999):05d}" if hasattr(self.beallitasok, 'rng') else None
            if kod is None:
                import random
                kod = f"{random.randint(0, 99999):05d}"
            if kod not in self.szobak:
                return kod
        raise RuntimeError("Nem sikerült szabad szobakódot találni.")

    async def _hiba_kuldes(self, websocket, uzenet: str):
        try:
            await websocket.send(json.dumps({"tipus": "hiba", "uzenet": uzenet}))
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    def _uj_szoba(self, jatek_mode, nehezseg_szint):
        while True:
            kod = f"{random.randint(0, 99999):05d}"
            if kod not in self.szobak:
                break
        szoba = SzobaAdat(kod, jatek_mode, nehezseg_szint, self.beallitasok)
        self.szobak[kod] = szoba
        szoba.jatek_task = asyncio.create_task(szoba.jatek_loop())
        print(f"[+] Új szoba: {kod} | mód: {jatek_mode} | nehézség: {nehezseg_szint}")
        return szoba

    async def _ures_szoba_takaritas(self, kod):
        szoba = self.szobak.get(kod)
        if szoba is None:
            return
        if szoba.kapcsolatok:
            return
        szoba.fut = False
        if szoba.jatek_task is not None:
            szoba.jatek_task.cancel()
            try:
                await szoba.jatek_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        self.szobak.pop(kod, None)
        print(f"[-] Szoba törölve: {kod}")

    async def kapcsolat_kezelo(self, websocket):
        kapcsolat = KapcsolatAdat(websocket)
        szoba = None
        try:
            elso = await websocket.recv()
            try:
                adat = json.loads(elso)
            except json.JSONDecodeError as hiba:
                await self._hiba_kuldes(websocket, "Hibás JSON belépési kérés.")
                print(hiba)
                return
            kapcsolat.ip_cim = adat.get("ip_cim")
            kapcsolat.nev = str(adat.get("nev", "Jatekos"))[:20] or "Jatekos"
            kapott_szin = adat.get("szin")
            if isinstance(kapott_szin, list) and len(kapott_szin) == 3:
                kapcsolat.szin = tuple(int(max(0, min(255, x))) for x in kapott_szin)
            else:
                kapcsolat.szin = SzinSeged.veletlen_szin()
            kapcsolat.szelesseg = int(adat.get("szelesseg", 1400))
            kapcsolat.magassag = int(adat.get("magassag", 830))

            tipus = adat.get("tipus", "")
            if tipus == "szoba_letrehozas":
                jatek_mode = str(adat.get("jatek_mode", "alma"))
                if jatek_mode not in ("alma", "tankos", "platformer"):
                    jatek_mode = "alma"
                nehezseg_szint = str(adat.get("nehezseg_szint", "Normal"))
                if nehezseg_szint not in ("Easy", "Normal", "Hard", "Nightmare", "Hell"):
                    nehezseg_szint = "Normal"
                szoba = self._uj_szoba(jatek_mode, nehezseg_szint)
            elif tipus == "szoba_csatlakozas":
                kod = str(adat.get("kod", ""))
                szoba = self.szobak.get(kod)
                if szoba is None:
                    await self._hiba_kuldes(websocket, "Nem létezik ilyen internetes szoba ezzel a kóddal.")
                    return
            else:
                await self._hiba_kuldes(websocket, "Ismeretlen belépési kérés.")
                return
            tank = adat.get("kep", None)
            await szoba.jatekos_hozzaadasa(kapcsolat, tank)
            init = {
                "tipus": "init",
                "sajat_id": kapcsolat.azonosito,
                "szoba_kod": szoba.kod,
                "jatek_mode": szoba.jatek_mode,
                "nehezseg_szint": szoba.nehezseg_szint,
            }
            await websocket.send(json.dumps(init))
            print(f"[+] Csatlakozott: {kapcsolat.azonosito} - {kapcsolat.nev}, ip cím: {kapcsolat.ip_cim} | szoba: {szoba.kod} | játékosok: {len(szoba.kapcsolatok)}")

            async for uzenet in websocket:
                try:
                    adat = json.loads(uzenet)
                except json.JSONDecodeError:
                    continue

                tipus = adat.get("tipus", "")
                if tipus == "irany" and szoba.jatek_mode == "alma":
                    szoba.vilag.jatekos_irany_beallitasa(kapcsolat.azonosito, float(adat.get("dx", 0.0)), float(adat.get("dy", 0.0)))
                elif tipus == "sebesseg" and szoba.jatek_mode == "alma":
                    szoba.vilag.jatekos_gyorsitas_beallitasa(kapcsolat.azonosito, bool(adat.get("gyors", False)))
                elif tipus == "mozgas" and szoba.jatek_mode in ["tankos", "platformer"]:
                    szoba.vilag.mozgas_beallitas(
                        kapcsolat.azonosito,
                        bool(adat.get("balra", False)),
                        bool(adat.get("jobbra", False)),
                        bool(adat.get("fel", False)),
                        bool(adat.get("le", False)),
                        bool(adat.get("loves", False)),
                        bool(adat.get("ugras", False))
                    )
                elif tipus == "kep_beallitas":
                    szoba.vilag.kep_meret_bealitas(adat.get("azonosito"), adat.get("width"), adat.get("height"), adat.get("x"), adat.get("y"))
                elif tipus == "atmeretezes":
                    kapcsolat.szelesseg = int(adat.get("szelesseg", kapcsolat.szelesseg))
                    kapcsolat.magassag = int(adat.get("magassag", kapcsolat.magassag))
                elif tipus == "ujraindulas":
                    szoba.vilag.folytatas(kapcsolat)
                elif tipus == "szobabol_kilepes":
                    await szoba.jatekos_torlese(kapcsolat.azonosito)
                elif tipus == "nev":
                    uj_nev = str(adat.get("nev", kapcsolat.nev))[:20] or kapcsolat.nev
                    kapcsolat.nev = uj_nev
                    if kapcsolat.azonosito in szoba.vilag.jatekosok:
                        szoba.vilag.jatekosok[kapcsolat.azonosito].nev = uj_nev
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as exc:
            print(f"[!] Kapcsolati hiba: {exc}")
        finally:
            if kapcsolat.azonosito and szoba is not None:
                await szoba.jatekos_torlese(kapcsolat.azonosito)
                print(f"[-] Kilépett: {kapcsolat.azonosito} | szoba: {szoba.kod} | maradt: {len(szoba.kapcsolatok)}")
                await self._ures_szoba_takaritas(szoba.kod)

    async def futtat(self):
        print(f"Központi szerver indul → ws://{self.host}:{self.port}")
        async with websockets.serve(self.kapcsolat_kezelo, self.host, self.port, ping_interval=None):
            await asyncio.Future()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8765)))
    args = parser.parse_args()

    szerver = KozpontiSzerver(args.host, args.port)
    asyncio.run(szerver.futtat())



main()
