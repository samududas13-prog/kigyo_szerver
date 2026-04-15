import argparse
import asyncio
import json
from typing import Dict, Optional
import socket
import websockets
import os
from kozos_jatekmag import Beallitasok, SzinSeged, VilagAllapot



class KapcsolatAdat:
    def __init__(self, websocket):
        self.websocket = websocket  # Az adott kliens websocket kapcsolata.
        self.azonosito = ""  # A kliens egyedi azonosítója a szerveren belül.
        self.szoba_kod = ""  # Annak a szobának a kódja, amelyben a kliens játszik.
        self.nev = ""  # A kliens által választott megjelenített név.
        self.szin = (200, 200, 200)  # A klienshez tartozó szín.
        self.szelesseg = 1400  # A kliens ablakának szélessége a személyre szabott nézethez.
        self.magassag = 830  # A kliens ablakának magassága a személyre szabott nézethez.
        self.ip_cim = ""
        self.csatlakozott = False  # Jelzi, hogy a teljes belépési kézfogás már lefutott-e.


class SzobaAdat:
    def __init__(self, kod: str, jatek_mode: str, nehezseg_szint: str, beallitasok: Beallitasok):
        self.kod = kod  # Az internetes szoba 5 jegyű kódja.
        self.jatek_mode = jatek_mode  # Az adott szobában futó játékmód.
        self.nehezseg_szint = nehezseg_szint  # Az adott szobában futó nehézségi szint.
        self.beallitasok = beallitasok  # A teljes világ- és hálózati konfiguráció közös példánya.
        self.vilag = VilagAllapot(beallitasok, jatek_mode, nehezseg_szint)  # A szoba közös, szerveroldali világállapota.
        self.kapcsolatok: Dict[str, KapcsolatAdat] = {}  # Az aktív kliensek kapcsolati adatai azonosító szerint.
        self.fut = True  # Jelzi, hogy a szoba saját játékciklusa fusson-e.
        self.kovetkezo_azonosito = 1  # Sorszámláló az új játékosazonosítókhoz.
        self.jatek_task: Optional[asyncio.Task] = None  # A szoba háttérben futó frissítő taskja.

    def uj_azonosito(self) -> str:
        azonosito = f"jatekos_{self.kovetkezo_azonosito}"
        self.kovetkezo_azonosito += 1
        return azonosito

    async def jatek_loop(self) -> None:
        while self.fut:
            await asyncio.sleep(1 / self.beallitasok.szerver_fps)
            self.vilag.frissites()

            bontando_azonositok = []
            for azonosito, kapcsolat in list(self.kapcsolatok.items()):
                if not kapcsolat.csatlakozott:
                    continue
                if azonosito not in self.vilag.jatekosok:
                    # akkor is küldünk állapotot!
                    allapot = self.vilag.nezet_jatekosnak(azonosito, kapcsolat.szelesseg, kapcsolat.magassag)
                    uzenet = json.dumps({"tipus": "allapot", "allapot": allapot})
                    try:
                        await kapcsolat.websocket.send(uzenet)
                    except Exception:
                        bontando_azonositok.append(azonosito)
                    continue
                else:
                    allapot = self.vilag.nezet_jatekosnak(azonosito, kapcsolat.szelesseg, kapcsolat.magassag)
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

    async def jatekos_hozzaadasa(self, kapcsolat: KapcsolatAdat) -> str:
        kapcsolat.azonosito = self.uj_azonosito()
        kapcsolat.szoba_kod = self.kod
        kapcsolat.csatlakozott = True
        self.kapcsolatok[kapcsolat.azonosito] = kapcsolat
        self.vilag.jatekos_hozzaadasa(kapcsolat.azonosito, kapcsolat.nev, kapcsolat.szin)
        return kapcsolat.azonosito

    async def jatekos_torlese(self, azonosito: str) -> None:
        kapcsolat = self.kapcsolatok.pop(azonosito, None)
        self.vilag.jatekos_torlese(azonosito)
        if kapcsolat is not None:
            try:
                await kapcsolat.websocket.close()
            except Exception:
                pass


class KozpontiSzerver:
    def __init__(self, host: str, port: int):
        self.host = host  # Az a hálózati cím, amelyre a websocket szerver bindol.
        self.port = port  # Az internetes websocket szerver portja.
        self.beallitasok = Beallitasok()  # A világlogikához és a szobakódokhoz használt közös beállítások.
        self.szobak: Dict[str, SzobaAdat] = {}  # Az aktív internetes szobák kód -> szoba leképezése.

    def _veletlen_kod(self) -> str:
        for _ in range(100000):
            kod = f"{self.beallitasok.rng.randint(0, 99999):05d}" if hasattr(self.beallitasok, 'rng') else None
            if kod is None:
                import random
                kod = f"{random.randint(0, 99999):05d}"
            if kod not in self.szobak:
                return kod
        raise RuntimeError("Nem sikerült szabad szobakódot találni.")

    async def _hiba_kuldes(self, websocket, uzenet: str) -> None:
        try:
            await websocket.send(json.dumps({"tipus": "hiba", "uzenet": uzenet}))
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    def _uj_szoba(self, jatek_mode: str, nehezseg_szint: str) -> SzobaAdat:
        import random
        while True:
            kod = f"{random.randint(0, 99999):05d}"
            if kod not in self.szobak:
                break
        szoba = SzobaAdat(kod, jatek_mode, nehezseg_szint, self.beallitasok)
        self.szobak[kod] = szoba
        szoba.jatek_task = asyncio.create_task(szoba.jatek_loop())
        print(f"[+] Új szoba: {kod} | mód: {jatek_mode} | nehézség: {nehezseg_szint}")
        return szoba

    async def _ures_szoba_takaritas(self, kod: str) -> None:
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
            except Exception:
                pass
        self.szobak.pop(kod, None)
        print(f"[-] Szoba törölve: {kod}")

    async def kapcsolat_kezelo(self, websocket) -> None:
        print("[WS] Új kapcsolat érkezett")
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
                if jatek_mode not in ("alma", "patogos"):
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

            await szoba.jatekos_hozzaadasa(kapcsolat)
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
                elif tipus == "mozgas" and szoba.jatek_mode == "patogos":
                    szoba.vilag.pattogos_mozgas_beallitasa(
                        kapcsolat.azonosito,
                        bool(adat.get("balra", False)),
                        bool(adat.get("jobbra", False)),
                        bool(adat.get("fel", False)),
                        bool(adat.get("le", False)),
                    )
                elif tipus == "atmeretezes":
                    kapcsolat.szelesseg = int(adat.get("szelesseg", kapcsolat.szelesseg))
                    kapcsolat.magassag = int(adat.get("magassag", kapcsolat.magassag))
                elif tipus == "ujraindulas":
                    szoba.vilag.ujrainditas(kapcsolat)
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

    async def futtat(self) -> None:
        print(f"Központi szerver indul → ws://{self.host}:{self.port}")
        async with websockets.serve(
            self.kapcsolat_kezelo,
            self.host,
            self.port,
            ping_interval=None
        ):
            await asyncio.Future()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8765)))
    args = parser.parse_args()

    szerver = KozpontiSzerver(args.host, args.port)
    asyncio.run(szerver.futtat())


if __name__ == "__main__":
    main()
