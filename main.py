import asyncio
import json
import math
import os
import queue
import random
import threading
from typing import Tuple
import pygame
import websockets
import socket
from kozos_jatekmag import Beallitasok, SzinSeged, VilagAllapot, Vector, ldtk_terkep_betoltes
import copy
from datetime import datetime
pygame.mixer.init()

KOZPONTI_SZERVER_CIM = "ws://127.0.0.1:8765"
KOZPONTI_SZERVER_CIM = "ws://192.168.1.238:8765"
KOZPONTI_SZERVER_CIM = "wss://kigyo-szerver.onrender.com"



MENTES_FILE = os.path.join(os.path.dirname(__file__), "jatekos_adatok.json")

def mentes(adatok: dict):
    lista = []

    if os.path.exists(MENTES_FILE):
        try:
            with open(MENTES_FILE, "r", encoding="utf-8") as f:
                tartalom = f.read().strip()
                if tartalom:
                    beolvasott = json.loads(tartalom)

                    if isinstance(beolvasott, list):
                        lista = beolvasott
                    elif isinstance(beolvasott, dict):
                        lista = [beolvasott]
        except json.JSONDecodeError:
            lista = []

    lista.append(adatok)

    with open(MENTES_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

class tankik:
    def __init__(self):
        self.eredeti_kepek = {
            "tank_1_kek": self.kep_betolto("tank_1_jo.png"),
            "tank_2_kek": self.kep_betolto("tank_3_jo.png"),
            "tank_3_kek": self.kep_betolto("tank_5_jo.png"),
            "tank_4_kek": self.kep_betolto("tank_7_jo.png"),
        }
        self.kepek = self.eredeti_kepek.copy()
        self.tank = "tank_1_kek"
        self.sebesseg = 10
        self.sebzes = 1
        self.hp = 2

    def tankok_meretezese_szinezese(self, szelesseg=60, szin=(200, 200, 200)):
        for i in self.eredeti_kepek:
            kep = self.eredeti_kepek[i]
            arany = szelesseg / kep.get_width()
            uj_magassag = int(kep.get_height() * arany)

            kep = pygame.transform.scale(kep, (szelesseg, uj_magassag))
            kep = self.tank_szinezese(kep, szin)
            self.kepek[i] = kep 

    def kep_betolto(self, nev):
        return pygame.image.load(os.path.join(os.path.dirname(__file__), "tankok", nev)).convert_alpha()
        
    def tank_rajzolas(self, screen, x, y, kamera_x=0, kamera_y=0, forgatas=0,melyik=""):
        if melyik == "":
            kep = pygame.transform.rotate(self.kepek[self.tank], -forgatas)
            screen.blit(kep, (int(x - kamera_x - kep.get_width() // 2), int(y - kamera_y - kep.get_height() // 2)))
        else:
            kep = pygame.transform.rotate(self.kepek[melyik], -forgatas)
            screen.blit(kep, (int(x - kamera_x - kep.get_width() // 2), int(y - kamera_y - kep.get_height() // 2)))
    
    def tank_szinezese(self, alap_kep, szin):
        kep = alap_kep.copy()

        for x in range(kep.get_width()):
            for y in range(kep.get_height()):
                r, g, b, a = kep.get_at((x, y))

                if a == 0:
                    continue

                max_szin = max(r, g, b)
                min_szin = min(r, g, b)

                if max_szin < 45:
                    continue

                if max_szin - min_szin < 25:
                    continue

                fenyesseg = max_szin / 255

                uj_r = int(szin[0] * (0.35 + fenyesseg * 0.65))
                uj_g = int(szin[1] * (0.35 + fenyesseg * 0.65))
                uj_b = int(szin[2] * (0.35 + fenyesseg * 0.65))

                kep.set_at((x, y), (uj_r, uj_g, uj_b, a))

        return kep
    
    def tank_valasztas(self, tank_nev):
        if tank_nev in self.kepek:
            self.tank = tank_nev

class Buff:
    def __init__(self):
        self.b = Beallitasok()
        self.szelesseg = self.b.buffok_szelesege
        self.buff_kepek = {
            "teleport": self.kep_betolto("teleport.png"),

            "hp": self.kep_betolto("hp.png"),
            "hp+": self.kep_betolto("hp+.png"),
            "hp-": self.kep_betolto("hp-.png"),

            "kill": self.kep_betolto("kill.png"),
            "kill-": self.kep_betolto("kill-.png"),
            "kill+": self.kep_betolto("kill+.png"),

            "bulet": self.kep_betolto("bulet.png"),
            "bulet-": self.kep_betolto("bulet-.png"),
            "bulet+": self.kep_betolto("bulet+.png"),

            "rotate": self.kep_betolto("rotate.png"),
            "rotate-": self.kep_betolto("rotate-.png"),
            "rotate+": self.kep_betolto("rotate+.png"),

            "shild": self.kep_betolto("shild.png"),
            "shild-": self.kep_betolto("shild-.png"),
            "shild+": self.kep_betolto("shild+.png"),

            "speed": self.kep_betolto("speed.png"),
            "speed-": self.kep_betolto("speed-.png"),
            "speed+": self.kep_betolto("speed+.png"),
        }
        
    def hud_buff_rajzolas(self, screen, nev, kozep_x, kozep_y, meret=48):
        kep = self.buff_kepek.get(nev)

        if kep is None:
            return

        arany = meret / max(kep.get_width(), kep.get_height())

        uj_szelesseg = max(1, int(kep.get_width() * arany))
        uj_magassag = max(1, int(kep.get_height() * arany))

        kep = pygame.transform.smoothscale(
            kep,
            (uj_szelesseg, uj_magassag)
        )

        screen.blit(
            kep,
            (
                int(kozep_x - kep.get_width() // 2),
                int(kozep_y - kep.get_height() // 2),
            )
        )
        
    def kep_betolto(self, nev):
        kep = pygame.image.load(os.path.join(os.path.dirname(__file__), "buffok", nev)).convert_alpha()
        arany = self.szelesseg / kep.get_width()
        uj_magassag = int(kep.get_height() * arany)

        return pygame.transform.scale(kep, (self.szelesseg, uj_magassag))
    
    def buff_rajzolas(self, screen, kep, x, y, kamera_x=0, kamera_y=0, forgatas=0):
        
            kep = pygame.transform.rotate(self.buff_kepek[kep], -forgatas)
            screen.blit(kep, (int(x - kamera_x - kep.get_width() // 2), int(y - kamera_y - kep.get_height() // 2)))
    
class P_eloleny:
    def __init__(self, kep, golem=1):
        self.path_to_golems = os.path.join(os.path.dirname(__file__), "tiles", "platformer", "golem", "Golem_" + str(golem))
        fielok = os.walk(self.path_to_golems)
        fileok1 = []
        for i in fielok:
                    fileok1.append(i)

        akciok = fileok1[0][1]
        fileok1 = fileok1[1:]
        szotar = {}
        torlo = []
        for index, i in enumerate(fileok1):
            if i == []:
                torlo.append(index)

        for i in torlo[:-1]:
            del fileok1[i]

        for i, j in enumerate(akciok):
            szotar[j] = fileok1[i][2:]


       
        self.kepek = {}
        for nev, adat in szotar.items():
            adatok = []
            for i in adat[0]:
                j = self.kep_betolto(os.path.join(nev, i))
                adatok.append(j)
            adatok = self.kep_szerkesztes(adatok)

            self.kepek[nev]=adatok
        print(akciok)
        
        
        self.mozgas_szamlalo = 0
        self.pot_mozgas_szamlalo = 0
        self.moz_szamlalo = 0
        self.elozo_mozgas_szamlalo = "Idle"
        self.max_szamlalo = len(self.kepek["Idle"])
        self.pot_max_szamlalo = 0
        self.irany = 1
        

    def kep_betolto(self, nev, szelesseg=100):
            kep = pygame.image.load(os.path.join(self.path_to_golems, nev)).convert_alpha()
            arany = szelesseg / kep.get_width()
            uj_magassag = int(kep.get_height() * arany)

            kep = pygame.transform.scale(kep, (szelesseg, uj_magassag))
            return kep

    def kep_szerkesztes(self, kepek):
        combined_rect = None
        for kep in kepek:
            box = kep.get_bounding_rect()
            if combined_rect == None:
                combined_rect = box.copy()
            else:
                combined_rect.union_ip(box)
        images = []
        for i, img in enumerate(kepek):
            surf = img.subsurface(combined_rect).copy()
            images.append(surf)
            pygame.image.save(surf, f"idle_golem_{i}")
        return images

    def rajzolas(self, screen, x, y, kamera_x=0, kamera_y=-1, forgatas=0, melyik="Idle"):
            k = True
            if self.elozo_mozgas_szamlalo != melyik:
                self.elozo_mozgas_szamlalo = melyik
                self.max_szamlalo = len(self.kepek[melyik])
                self.mozgas_szamlalo = 0

            if self.moz_szamlalo % 2 == 0:
                self.mozgas_szamlalo += 1
                

            if self.mozgas_szamlalo >= self.max_szamlalo and melyik != "Jump Start":
                self.mozgas_szamlalo = 0
            

            elif self.mozgas_szamlalo >= self.max_szamlalo and melyik == "Jump Start":
                self.pot_max_szamlalo = len(self.kepek["Jump Loop"])
                melyik = "Jump Loop"
                k = False
                if self.moz_szamlalo % 3 == 0:
                    self.pot_mozgas_szamlalo += 1
                if self.pot_mozgas_szamlalo >= self.pot_max_szamlalo:
                     self.pot_mozgas_szamlalo = 0
                    
            
            if forgatas == 0:
                pass
            else: 
                self.irany = forgatas
            

            
            
            
            kep = pygame.transform.flip(self.kepek[melyik][self.mozgas_szamlalo if k else self.pot_mozgas_szamlalo], True if self.irany == -1 else False, False)
            screen.blit(kep, (int(x - kamera_x), int(y - kamera_y )))

            self.moz_szamlalo += 1

class Kepernyo_tank:
    def __init__(self, tank_kep, szin):
        self.kep = tank_kep
        self.szin = szin
        self.tank_szinezese(self.kep, self.szin)

    def tank_rajzolas(self, screen, x, y, kamera_x=0, kamera_y=0, forgatas=0,):
        kep = pygame.transform.rotate(self.kep, -forgatas)
        screen.blit(kep, (int(x - kamera_x - kep.get_width() // 2), int(y - kamera_y - kep.get_height() // 2)))
       
    
    def tank_szinezese(self, alap_kep, szin):
        kep = self.kep

        for x in range(kep.get_width()):
            for y in range(kep.get_height()):
                r, g, b, a = kep.get_at((x, y))

                if a == 0:
                    continue

                max_szin = max(r, g, b)
                min_szin = min(r, g, b)

                if max_szin < 45:
                    continue
                    
                if max_szin - min_szin < 25:
                    continue

                fenyesseg = max_szin / 255

                uj_r = int(szin[0] * (0.35 + fenyesseg * 0.65))
                uj_g = int(szin[1] * (0.35 + fenyesseg * 0.65))
                uj_b = int(szin[2] * (0.35 + fenyesseg * 0.65))

                kep.set_at((x, y), (uj_r, uj_g, uj_b, a))

        self.kep
    

class HalozatiKliens:
    def __init__(self, szerver_cim: str, belepesi_mod: str, szoba_kod: str, jatek_mode: str, nehezseg_szint: str, nev: str, szin: Tuple[int, int, int], szelesseg: int, magassag: int, ip_cim: str, kep=None):
        self.szerver_cim = szerver_cim  
        self.belepesi_mod = belepesi_mod
        self.szoba_kod = szoba_kod
        self.jatek_mode = jatek_mode 
        self.nehezseg_szint = nehezseg_szint 
        self.nev = nev
        self.szin = szin 
        self.nezet_szelesseg = int(szelesseg)
        self.nezet_magassag = int(magassag)
        self.kuldes_sor = queue.Queue(maxsize=120)
        self.fogadas_sor = queue.Queue(maxsize=10)
        self.sajat_id = None
        self.ip_cim = ip_cim
        self.csatlakozva = False
        self.fut = True
        self.hiba = "" 
        self.init_megkapva = False  
        self._szal = threading.Thread(target=self._indit, daemon=True) 
        self.kep = kep
        
    def indit(self):
        self._szal.start()

    def leallit(self):
        self.fut = False

    def kuldd(self, adat: dict):
        if not self.fut:
            return
        try:
            self.kuldes_sor.put_nowait(adat)
        except queue.Full:
            pass

    def legfrissebb_allapot(self):
        utolso = None
        while True:
            try:
                utolso = self.fogadas_sor.get_nowait()
            except queue.Empty:
                break
        return utolso

    def _indit(self):
        asyncio.run(self._ws_loop())

    async def _ws_loop(self):
        probak = 0
        while self.fut and probak < 20:
            try:
                async with websockets.connect(self.szerver_cim, max_size=2**22) as ws:
                    self.csatlakozva = True
                    if self.belepesi_mod == "create":
                        belepes = {
                            "tipus": "szoba_letrehozas",
                            "nev": self.nev,
                            "szin": list(self.szin),
                            "jatek_mode": self.jatek_mode,
                            "nehezseg_szint": self.nehezseg_szint,
                            "szelesseg": self.nezet_szelesseg,
                            "magassag": self.nezet_magassag,
                            "ip_cim": self.ip_cim,
                            "kep": self.kep,
                        }
                    else:
                        belepes = {
                            "tipus": "szoba_csatlakozas",
                            "kod": self.szoba_kod,
                            "nev": self.nev,
                            "szin": list(self.szin),
                            "szelesseg": self.nezet_szelesseg,
                            "magassag": self.nezet_magassag,
                            "ip_cim": self.ip_cim,
                            "kep": self.kep,
                        }
                    await ws.send(json.dumps(belepes))

                    async def fogado():
                        async for uzenet in ws:
                            try:
                                adat = json.loads(uzenet)
                            except json.JSONDecodeError:
                                continue
                            tipus = adat.get("tipus")
                            if tipus == "init":
                                self.sajat_id = adat.get("sajat_id")
                                self.szoba_kod = str(adat.get("szoba_kod", self.szoba_kod))
                                self.jatek_mode = str(adat.get("jatek_mode", self.jatek_mode))
                                self.nehezseg_szint = str(adat.get("nehezseg_szint", self.nehezseg_szint))
                                self.init_megkapva = True
                            
                            elif tipus == "allapot":
                                if self.fogadas_sor.full():
                                    try:
                                        self.fogadas_sor.get_nowait()
                                    except queue.Empty:
                                        pass
                                try:
                                    self.fogadas_sor.put_nowait(adat.get("allapot", {}))
                                except queue.Full:
                                    pass
                                
                            elif tipus == "hiba":
                                self.hiba = str(adat.get("uzenet", "Ismeretlen szerverhiba"))
                                print(self.hiba)
                                self.fut = False
                                try:
                                    await ws.close()
                                except Exception:
                                    pass
                                return

                    async def kuldo():
                        while self.fut:
                            await asyncio.sleep(1 / 120)
                            while not self.kuldes_sor.empty():
                                try:
                                    adat = self.kuldes_sor.get_nowait()
                                except queue.Empty:
                                    break
                                await ws.send(json.dumps(adat))

                    await asyncio.gather(fogado(), kuldo())
                    return
            except Exception as h:
                self.hiba = str(h)
                probak += 1
                print(h)
                await asyncio.sleep(0.35)
        self.csatlakozva = False


class Alap:
    MENTES_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
    def __init__(self):
        pygame.init()
        self.picture_of_golems = []
        for i in range(1, 4):
            print(i)
            self.picture_of_golems.append(self.kep_betolto(os.path.join(os.path.dirname(__file__), "tiles", "platformer", "golem", "Golem_" + str(i), "Idle"), "0_Golem_Idle_000.png"))
        self.picture_of_golems = self.kep_korbe_vagasa(self.picture_of_golems)
        self.golem_valaszto_gombok = {}
        for index, i in enumerate(self.picture_of_golems):
                    self.golem_valaszto_gombok[str(index)] = {"rect": None}
        self.path_settings_billentyu = os.path.join(os.path.dirname(__file__), "billentyu_beallitasok.json")
        self.path_hatter = os.path.join(os.path.dirname(__file__), "tiles", "platformer", "erdos", "Background", "1920x1080")
        self.hatter = self.kep_betolto(self.path_hatter, "hatter.png")
        self.hatter = pygame.transform.scale(self.hatter, (1920, 1080))
        self.settings_data = self.settings_load()
        self.beallitasok = Beallitasok()
        self.is_mobile = 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_BOOTLOGO' in os.environ
        self.szeleseg = self.settings_data["ablak_szelesseg"] or 1300 
        self.magassag = self.settings_data["ablak_magassag"] or 700
        self.platformer_zoom = self.beallitasok.platformer_zoom
        self.platformer_halozat_meretezes = False

        if self.is_mobile:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.szeleseg, self.magassag = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((self.szeleseg, self.magassag), pygame.FULLSCREEN if self.settings_data["teljeskepernyo"] == 1 else pygame.RESIZABLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.elozo_statusz = "home"
        self.statusz = "home"
        self.paused = False
        self.kamera_x = 0.0 
        self.kamera_y = 0.0
        self.font_nagy = pygame.font.Font(None, 42)  
        self.font_kozep = pygame.font.Font(None, 30) 
        self.font_kis = pygame.font.Font(None, 22)
        self.font_mini = pygame.font.Font(None, 18)

        self.nev = self.settings_data["nev"] or "" 
        self.aktiv_nev_szovegdoboz = False
        self.nev_szoveg_rect = None 
        self.jatek_mode = self.settings_data["jatek_mode"] or "tankos" 
        self.nehezseg_szint = self.settings_data["nehezseg_szint"] or "Normal"
        self.halozati_mod = "single" 
        self.home_hiba = "" 
        self.varakozas_szoveg = "" 
        self.szoba_kod = "" 
        self.szoba_kod_aktiv = False 
        self.szoba_kod_rect = None
        self.settings_szoveg_rect = None


        self.tiles = os.path.join(os.path.dirname(__file__), "tiles")
        self.talaj = os.path.join(self.tiles, "talaj")
        self.falak = os.path.join(self.tiles, "falak")
        self.kovek = os.path.join(self.tiles, "kovek")
        self.chest = os.path.join(self.tiles, "chest")

        self.hangok = os.path.join(os.path.dirname(__file__), "hangok")
        self.loves = os.path.join(self.hangok, "tank_loves")
        self.background = os.path.join(self.hangok, "bacground")
        self.hangok = {
            "sima_tank_loves": self.hang_betolto(self.loves, "sima_tank_loves.mp3"),
            "bacground": {
                1: self.hang_betolto(self.background, "mousick1.mp3"),
                2: self.hang_betolto(self.background, "mousick2.mp3"),
                3: self.hang_betolto(self.background, "mousick3.mp3"),
                4: self.hang_betolto(self.background, "mousick4.mp3"),
                5: self.hang_betolto(self.background, "mousick5.mp3"),
                6: self.hang_betolto(self.background, "mousick6.mp3"),
            }
        }
        self.background_musick = pygame.mixer.Channel(0)
        self.background_musick_count = 1

        self.talaj_kepek = {
            "koves": [self.kep_betolto(self.talaj, "koves_1.png"), self.kep_betolto(self.talaj, "koves_2.png")],
            "fuves": [self.kep_betolto(self.talaj, "fuves_1.png"), self.kep_betolto(self.talaj, "fuves_2.png")],
            "fold": [self.kep_betolto(self.talaj, "fold_1.png"), self.kep_betolto(self.talaj, "fold_2.png")],
            "chest": self.kep_betolto(self.chest, "chest1.png")
        }
        self.fal_kepek = {
            "bal_fent": self.kep_betolto(self.falak, "kofal_bal_felul.png"),
            "fent": self.kep_betolto(self.falak, "kofal_felul.png"),
            "jobb_fent": self.kep_betolto(self.falak, "kofal_jobb_felul.png"),
            "bal": self.kep_betolto(self.falak, "kofal_bal.png"),
            "kozep": self.kep_betolto(self.falak, "kofal.png"),
            "jobb": self.kep_betolto(self.falak, "kofal_jobb.png"),
            "bal_lent": self.kep_betolto(self.falak, "kofal_bal_alul.png"),
            "lent": self.kep_betolto(self.falak, "kofal_alul.png"),
            "jobb_lent": self.kep_betolto(self.falak, "kofal_jobb_alul.png"),
            "fent_lent": self.kep_betolto(self.falak, "kofal_fent_lent.png"),
            "bal_jobb": self.kep_betolto(self.falak, "kofal_bal_jobb.png"),
            "3_alul": self.kep_betolto(self.falak, "kofal_oldalt_alul.png"),
            "3_balra": self.kep_betolto(self.falak, "kofal_oldalt_bal.png"),
            "3_fent": self.kep_betolto(self.falak, "kofal_oldalt_fent.png"),
            "3_jobbra": self.kep_betolto(self.falak, "kofal_oldalt_jobb.png"),
            "kovek": [self.kep_betolto(self.kovek, "sima_ko_1.png"), self.kep_betolto(self.kovek, "sima_ko_2.png"), self.kep_betolto(self.kovek, "sima_ko_3.png")],

        }
        
        
        
        
        
        self.volt_irany_x = 0.0
        self.volt_irany_y = 0.0
        self.volt_gyors = False
        self.fel = False
        self.jobb = False
        self.le = False
        self.bal = False
        self.tank = tankik()
        self.tank.tank = self.settings_data["tank"]
        self.tank_szog = 0
        self.tank_valaszto_gombok = {}
        for i in self.tank.kepek:
            self.tank_valaszto_gombok[i] = {"rect": None}

        
        self.fej_x, self.fej_y = 0, 0
        self.koordinata_szoveg = ""
        self.pontszam = 0
        self.testhossz = 0
        self.olesek = 0
        self.ido = 0
        self.hp = 0
        self.uj_buffok = {}

        self.ellenseg_tankok = {}
        
        self.rangsor = []
        
        self.mentes_megtortent_e = False
        self.halal_allapot = None
        
        self.regi = {}
        
        
        self.szin = self.settings_data["szin"] or SzinSeged.veletlen_szin()
        self.szin_beallitasok = {
            "szin_1": {"rect": None, "ertek": str(self.szin[0]), "aktiv": False},
            "szin_2": {"rect": None, "ertek": str(self.szin[1]), "aktiv": False},
            "szin_3": {"rect": None, "ertek": str(self.szin[2]), "aktiv": False},
        } 
        self.jatek_mode_valasztas = {
            "alma": {"rect": None},
            "tankos": {"rect": None},
            "platformer": {"rect": None}
        }
        self.neheyseg_gombok = {
            "Easy": {"rect": None},
            "Normal": {"rect": None},
            "Hard": {"rect": None},
            "Nightmare": {"rect": None},
            "Hell": {"rect": None},
        }
        self.inditasi_gombok = {
            "single": {"rect": None, "felirat": "Egyszemélyes"},
            "create": {"rect": None, "felirat": "Create"},
            "join": {"rect": None, "felirat": "Join"},
        } 
        self.pause_gomb = pygame.Rect(10, 10, self.beallitasok.pause_gomb_szelesseg, self.beallitasok.pause_gomb_magassag)  
        self.pause_gombok = {
            "resume": {"rect": None},
            "main menu": {"rect": None},
            "new game": {"rect": None},
            "settings": {"rect": None},
        } 
        self.ujraindulas_gomb = None
        self.kilepes_gomb = None
        self.ranglistak_rect = None
        self.golem = self.settings_data.get("golem", "1")

        self.ranglista_adatok = []
        self.ranglista_scroll = 0

        self.ranglista_mode_szuro = "all"
        self.ranglista_nehezseg_szuro = "all"
        self.ranglista_nev_szuro = "all"

        self.ranglista_rendezes = "pontszam"
        self.ranglista_csokkeno = True

        self.ranglista_nev_aktiv = False

        self.ranglista_vissza_rect = None
        self.ranglista_mode_rect = None
        self.ranglista_nehezseg_rect = None
        self.ranglista_nev_rect = None
        self.ranglista_rendezes_rect = None
        self.ranglista_irany_rect = None
        self.ranglista_frissites_rect = None

        self.halozat_volt_loves = False

        self.uj_buffok = {} # [mennyi van még hatra, buff név, negativ/pozitiv, ertek]
        self.uj_buffok_torlese = []

        self.vilag_szeleseg = self.beallitasok.tank_vilag_szelesseg
        self.vilag_magassag = self.beallitasok.tank_vilag_magassag

        self.vilag_bealitas = {
            "szelesseg": {"rect": None, "ertek": self.settings_data["vilag_szelesseg"] or str(self.vilag_szeleseg), "aktiv": False, "szoveg": "világ szélessége:"},
            "magassag": {"rect": None, "ertek": self.settings_data["vilag_magassag"] or str(self.vilag_magassag), "aktiv": False, "szoveg": "világ magassaága:"},
            "AI_db": {"rect": None, "ertek": self.settings_data["AI_db"] or str(self.beallitasok.nehezseg_atvalto[self.nehezseg_szint]), "aktiv": False, "szoveg": "ellenség darabszám:"},
            }

        self.helyi_vilag = None 
        self.helyi_jatekos_id = "helyi_jatekos" 
        self.halozat = None
        self.utolso_allapot = None 
        self.kliens_seged_vilag = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip_cim = s.getsockname()[0]
            s.close()
        except:
            self.ip_cim = "Az ip címet nem sikerült lekérni"
        pygame.display.set_caption("Játék")

        self.buffok = None
        self.mousick_settings = self.settings_data["mousick_settings"] or {
            "backround_mousick": 0.4,
            "tank_loves": 1,
        }
        self.background_musick.set_volume(float(self.mousick_settings["backround_mousick"]))

        self.hangok["sima_tank_loves"].set_volume(float(self.mousick_settings["tank_loves"]))
        self.settings_oldalak = {
            "Hangok": {
                "rect": None,
                "klikd": True,
            },
            "Billentyű": {
                "rect": None,
                "klikd": False,
            }
        }

        self.settings_billentyu_modok = {
            i: {"rect": None, "klikd": False} for i in self.jatek_mode_valasztas.keys()
        }
        self.settings_billentyu_modok["platformer"]["klikd"] = True
        self.bilentyu_klikd = None
        self.billentyu_kiosztas = self.billentyu_json()
        self.billentyu_rectek = {
            bill: {"rect": None, "klikd": False}  for bill in self.billentyu_kiosztas["platformer"].keys()
        }

        self.settings_slider_rectek = {}
        self.settings_huzott = None
        self.settings_vissza = None

        
        self.mobil_valaszto_rect = pygame.Rect(30, 80, 160, 42) 

        
        self.joystick_kozep = (150, 550)
        self.joystick_sugar = 75
        self.gomb_kozep = (1150, 550)
        self.gomb_sugar = 55

        
        self.ujjak = {}

        
        self.joystick_irany_x = 0.0
        self.joystick_irany_y = 0.0
        self.mobil_loves = False
        if self.is_mobile:
            self._mobil_gombok_frissitese()

        self.platformer_file_helye = os.path.join(os.path.dirname(__file__), "platformer_szobak")
        self.jelenlegi_szoba = self.settings_data.get("platformer").get("jelenlegi_szoba", "1_kezdo_szoba.json")
        self.elozo_jelenlegi_szoba = ""
        self.platformer_terkep = None

        self.kamera_vel = Vector(0, 0)
        self.eltolodott_kamera_x = self.kamera_x
        self.eltolodott_kamera_y = self.kamera_y
        
    def kep_korbe_vagasa(self, kepek):
            combined_rect = None
            for kep in kepek:
                box = kep.get_bounding_rect()
                if combined_rect == None:
                    combined_rect = box.copy()
                else:
                    combined_rect.union_ip(box)
            images = []
            for i, img in enumerate(kepek):
                surf = img.subsurface(combined_rect).copy()
                images.append(surf)
                pygame.image.save(surf, f"idle_golem_{i}")
            return images

    def _single_inditas(self):
        self._szin_frissites()
        self.helyi_vilag = VilagAllapot(self.beallitasok, self.jatek_mode, self.nehezseg_szint, vilag_szelesseg=self.vilag_bealitas["szelesseg"]["ertek"], vilag_magassag=self.vilag_bealitas["magassag"]["ertek"],ai_db=self.vilag_bealitas["AI_db"]["ertek"])
        nev = self.nev.strip() or "Jatekos"
        self.helyi_vilag.jatekos_hozzaadasa(self.helyi_jatekos_id, nev, self.szin, self.tank.tank)
        self.utolso_allapot = self.helyi_vilag.nezet_jatekosnak(self.helyi_jatekos_id, self.szeleseg, self.magassag)
        self.halozati_mod = "single"
        self.statusz = "jatek"
        self.paused = False
        self.elozo_jelenlegi_szoba = None
        self.home_hiba = ""
        self.halal_allapot = None
        self.mentes_megtortent_e = False
        if self.jatek_mode == "platformer":
            
            self._platformer_assets_brtoltes()
            self.helyi_vilag.kep_meret_bealitas(self.helyi_jatekos_id, "width", "height", "", self.jatekos.kepek["Idle"][0].get_width() / self.platformer_zoom, self.jatekos.kepek["Idle"][0].get_height() / self.platformer_zoom)

    def _multiplayer_inditas(self, mod: str):
        self._szin_frissites()
        self.halozati_mod = mod
        self.statusz = "varakozas"
        self.home_hiba = ""
        self.elozo_jelenlegi_szoba = None
        self.varakozas_szoveg = f"Kapcsolódás a szerverhez: {KOZPONTI_SZERVER_CIM}"
        self.halal_allapot = None
        self.kliens_seged_vilag = VilagAllapot(self.beallitasok, self.jatek_mode, self.nehezseg_szint)

        if mod == "join":
            if len(self.szoba_kod) != self.beallitasok.szoba_kod_hossz:
                self.home_hiba = "A szobakód 5 számjegy legyen."
                self.statusz = "home"
                return
        else:
            self.szoba_kod = ""

        self.halozat = HalozatiKliens(KOZPONTI_SZERVER_CIM, mod, self.szoba_kod, self.jatek_mode, self.nehezseg_szint, self.nev.strip() or "Jatekos",
                                      self.szin, self.szeleseg, self.magassag, self.ip_cim, self.tank.tank)
        self.halozat.indit()
        if self.jatek_mode == "platformer":
            self._platformer_assets_brtoltes()
                         
        self.mentes_megtortent_e = False

    def the_assets_are_loading(self):
        self.screen.fill((0,0,0))
        szoveg = self.font_nagy.render("THE ASSETS ARE LOADING\n please wait ......", True, (30, 255, 40))
        self.screen.blit(szoveg, (self.screen.get_width()//2-szoveg.get_width()//2, self.screen.get_height()//2-szoveg.get_height()//2))
        pygame.display.update()
    def kamera_mozgatasa(self, x, y):
        if self.eltolodott_kamera_x < x:
            self.kamera_vel.x = min(self.eltolodott_kamera_x + 5, 20)
        elif self.eltolodott_kamera_x > x:
            self.kamera_vel.x = max(self.eltolodott_kamera_x - 5, -20)
        if self.eltolodott_kamera_y < y:
            self.kamera_vel.y = min(self.eltolodott_kamera_y + 5, 20)
        elif self.eltolodott_kamera_y > y:
            self.kamera_vel.y = max(self.eltolodott_kamera_y - 5, -20)
        if self.eltolodott_kamera_x == x:
            self.kamera.vel.x = 0
        if self.eltolodott_kamera_y == y:
            self.kamera.vel.y = 0



        self.eltolodott_kamera_x += self.kamera_vel.x
        self.eltolodott_kamera_y += self.kamera_vel.y

    def settings_mentes(self):
        with open(Alap.MENTES_SETTINGS_FILE, "w", encoding="utf-8") as f:
            screen = pygame.display.get_surface()
            menteni_kivant = {
                "nev": self.nev,
                "jatek_mode": self.jatek_mode,
                "nehezseg_szint": self.nehezseg_szint,
                "vilag_szelesseg": self.vilag_bealitas["szelesseg"]["ertek"],
                "vilag_magassag": self.vilag_bealitas["magassag"]["ertek"],
                "AI_db": self.vilag_bealitas["AI_db"]["ertek"],
                "tank": self.tank.tank,
                "szin": self.szin,
                "mousick_settings": self.mousick_settings,
                "ablak_szelesseg": self.szeleseg,
                "ablak_magassag": self.magassag,
                "teljeskepernyo": 1 if bool(screen.get_flags() & pygame.FULLSCREEN) else 0,
                "szoba_kod": self.szoba_kod,
                "golem": self.golem,
                "platformer":{
                    "szoba": self.jelenlegi_szoba
                }
            }
            json.dump(menteni_kivant, f, indent=2, ensure_ascii=False)

    def settings_load(self):
        if os.path.exists(Alap.MENTES_SETTINGS_FILE
):
            with open(Alap.MENTES_SETTINGS_FILE, "r", encoding="utf-8") as f:
                tartalom = f.read().strip()
                return json.loads(tartalom)

    def _mobil_gombok_frissitese(self):
        self.joystick_kozep = (150, self.magassag - 140)
        self.gomb_kozep = (self.szeleseg - 150, self.magassag - 140)

    def _mobil_mod_be_ki(self):
        self.is_mobile = not self.is_mobile
        if self.is_mobile:
            info = pygame.display.Info()
            self.szeleseg = info.current_w
            self.magassag = info.current_h
            self.screen = pygame.display.set_mode((self.szeleseg, self.magassag), pygame.FULLSCREEN)
        else:
            self.szeleseg = self.settings_data["ablak_szelesseg"] or 1300 
            self.magassag = self.settings_data["ablak_magassag"] or 700
            self.screen = pygame.display.set_mode((self.szeleseg, self.magassag), pygame.FULLSCREEN if self.settings_data["teljeskepernyo"] == 1 else pygame.RESIZABLE)
            
        self._mobil_gombok_frissitese()
        if self.halozat:
            self.halozat.kuldd({"tipus": "atmeretezes", "szelesseg": self.szeleseg, "magassag": self.magassag})

    def hang_betolto(self, hely, nev):
        return pygame.mixer.Sound(os.path.join(hely, nev))#.set_volume(40)

    def kep_betolto(self, hely, nev):
        kep = pygame.image.load(os.path.join(hely, nev))#.convert_alpha()
        return pygame.transform.scale(kep,(90, 90))

    def _szamot_ertekre(self, szoveg):
        if szoveg.isdigit():
            return int(szoveg)
        return 0

    def _szin_frissites(self):
        self.szin = (
            max(0, min(255, self._szamot_ertekre(self.szin_beallitasok["szin_1"]["ertek"]))),
            max(0, min(255, self._szamot_ertekre(self.szin_beallitasok["szin_2"]["ertek"]))),
            max(0, min(255, self._szamot_ertekre(self.szin_beallitasok["szin_3"]["ertek"]))),
        )

    def _uj_szobakod(self):
        return f"{random.randint(0, 99999):05d}"

    def ranglistak_betoltese(self):
        self.statusz = "ranglistak"
        self.ranglista_scroll = 0
        self.ranglista_nev_aktiv = False
        self.ranglista_frissitese()

    def ranglista_szuro_lista(self, ertek):
        if ertek is None:
            return None

        if isinstance(ertek, list):
            lista = [str(x).strip().lower() for x in ertek if str(x).strip()]
        else:
            szoveg = str(ertek).strip()
            if szoveg.lower() == "all" or szoveg == "":
                return None
            lista = [x.strip().lower() for x in szoveg.split(",") if x.strip()]

        if not lista or "all" in lista:
            return None

        return lista

    def ranglista_datum_ertek(self, adat):
        ido_adat = adat.get("befejezesi_ido", {})

        if not isinstance(ido_adat, dict):
            return 0

        try:
            dt = datetime(
                int(ido_adat.get("ev", 2030)),
                int(ido_adat.get("honap", 0)),
                int(ido_adat.get("nap", 0)),
                int(ido_adat.get("ora", 0)),
                int(ido_adat.get("perc", 0)),
                int(ido_adat.get("masodperc", 0)),
                int(ido_adat.get("micromasodperc", 0)),
            )
            return dt.timestamp()
        except Exception:
            return 0

    def ranglista_datum_szoveg(self, adat):
        ido_adat = adat.get("befejezesi_ido", {})

        if not isinstance(ido_adat, dict):
            return "-"

        try:
            return (
                f"{int(ido_adat.get('ev', 0)):04d}."
                f"{int(ido_adat.get('honap', 0)):02d}."
                f"{int(ido_adat.get('nap', 0)):02d} "
                f"{int(ido_adat.get('ora', 0)):02d}:"
                f"{int(ido_adat.get('perc', 0)):02d}"
            )
        except Exception:
            return "-"

    def ranglista_rendezo_ertek(self, adat):
        if self.ranglista_rendezes == "datum":
            return self.ranglista_datum_ertek(adat)

        if self.ranglista_rendezes == "tulelesiido":
            return float(adat.get("ido", 0) or 0)

        if self.ranglista_rendezes == "pontszam":
            return int(adat.get("alma_pontszam", 0) or 0)

        if self.ranglista_rendezes == "olesek":
            return int(adat.get("olesek", 0) or 0)

        if self.ranglista_rendezes == "hosszusag":
            return int(adat.get("hoszusag", 0) or 0)

        return 0

    def ranglistak_beolvasasa(self, mode_szuro="all", nehezseg_szuro="all", nev_szuro="all", rendezes="pontszam",csokkeno=True):
        if not os.path.exists(MENTES_FILE):
            return []

        try:
            with open(MENTES_FILE, "r", encoding="utf-8") as f:
                tartalom = f.read().strip()

            if not tartalom:
                return []

            beolvasott = json.loads(tartalom)

            if isinstance(beolvasott, dict):
                adatok = [beolvasott]
            elif isinstance(beolvasott, list):
                adatok = beolvasott
            else:
                return []

        except Exception:
            return []

        mode_lista = self.ranglista_szuro_lista(mode_szuro)
        nehezseg_lista = self.ranglista_szuro_lista(nehezseg_szuro)
        nev_lista = self.ranglista_szuro_lista(nev_szuro)

        eredmeny = []

        for adat in adatok:
            if not isinstance(adat, dict):
                continue

            nev = str(adat.get("nev", "Jatekos")).strip()
            mode = str(adat.get("mode", "")).strip()
            nehezseg = str(adat.get("nehezseg", "")).strip()

            if mode_lista is not None and mode.lower() not in mode_lista:
                continue

            if nehezseg_lista is not None and nehezseg.lower() not in nehezseg_lista:
                continue

            if nev_lista is not None and nev.lower() not in nev_lista:
                continue

            eredmeny.append(adat)

        regi_rendezes = self.ranglista_rendezes
        self.ranglista_rendezes = rendezes

        eredmeny.sort(
            key=lambda adat: self.ranglista_rendezo_ertek(adat),
            reverse=csokkeno
        )

        self.ranglista_rendezes = regi_rendezes

        return eredmeny

    def ranglista_frissitese(self):
        self.ranglista_adatok = self.ranglistak_beolvasasa(mode_szuro=self.ranglista_mode_szuro, nehezseg_szuro=self.ranglista_nehezseg_szuro, nev_szuro=self.ranglista_nev_szuro, rendezes=self.ranglista_rendezes, csokkeno=self.ranglista_csokkeno,)

        if self.ranglista_scroll < 0:
            self.ranglista_scroll = 0

        max_scroll = max(0, len(self.ranglista_adatok) - 14)
        if self.ranglista_scroll > max_scroll:
            self.ranglista_scroll = max_scroll

    def ranglista_gomb(self, rect, szoveg, aktiv=False):
        szin = (70, 180, 255) if aktiv else (70, 70, 70)
        pygame.draw.rect(self.screen, szin, rect)
        pygame.draw.rect(self.screen, (230, 230, 230), rect, 2)

        felirat = self.font_kis.render(szoveg, True, (255, 255, 255))
        self.screen.blit(
            felirat,
            (
                rect.x + rect.w // 2 - felirat.get_width() // 2,
                rect.y + rect.h // 2 - felirat.get_height() // 2,
            )
        )

    def ranglistak_rajzolas(self):
        self.screen.fill((0, 0, 0))

        cim = self.font_nagy.render("RANGLISTA", True, (255, 80, 80))
        self.screen.blit(cim, (self.szeleseg // 2 - cim.get_width() // 2, 20))

        self.ranglista_vissza_rect = pygame.Rect(30, 25, 150, 45)
        self.ranglista_mode_rect = pygame.Rect(40, 95, 190, 42)
        self.ranglista_nehezseg_rect = pygame.Rect(250, 95, 210, 42)
        self.ranglista_nev_rect = pygame.Rect(480, 95, 280, 42)
        self.ranglista_rendezes_rect = pygame.Rect(780, 95, 230, 42)
        self.ranglista_irany_rect = pygame.Rect(1030, 95, 120, 42)
        self.ranglista_frissites_rect = pygame.Rect(1170, 95, 100, 42)

        self.ranglista_gomb(self.ranglista_vissza_rect, "Vissza")
        self.ranglista_gomb(self.ranglista_mode_rect, f"Mód: {self.ranglista_mode_szuro}")
        self.ranglista_gomb(self.ranglista_nehezseg_rect, f"Nehézség: {self.ranglista_nehezseg_szuro}")
        self.ranglista_gomb(self.ranglista_nev_rect, f"Név: {self.ranglista_nev_szuro}", self.ranglista_nev_aktiv)
        self.ranglista_gomb(self.ranglista_rendezes_rect, f"Rendezés: {self.ranglista_rendezes}")

        irany_szoveg = "↓" if self.ranglista_csokkeno else "↑"
        self.ranglista_gomb(self.ranglista_irany_rect, irany_szoveg)
        self.ranglista_gomb(self.ranglista_frissites_rect, "Frissít")


        fejlec_y = 190
        sor_magassag = 30

        fejlec = self.font_mini.render("hely   név                 mód       nehézség      túlélés     pont     ölés     hossz     dátum", True, (255, 230, 120))
        self.screen.blit(fejlec, (40, fejlec_y))

        start = self.ranglista_scroll
        vege = min(len(self.ranglista_adatok), start + 14)

        y = fejlec_y + 35

        if not self.ranglista_adatok:
            nincs = self.font_kozep.render("Nincs találat vagy nincs mentett adat.", True, (220, 220, 220))
            self.screen.blit(nincs, (self.szeleseg // 2 - nincs.get_width() // 2, self.magassag // 2))
            return

        for index in range(start, vege):
            adat = self.ranglista_adatok[index]

            nev = str(adat.get("nev", "Jatekos"))[:18]
            mode = str(adat.get("mode", "-"))[:8]
            nehezseg = str(adat.get("nehezseg", "-"))[:10]
            ido = float(adat.get("ido", 0) or 0)
            pont = int(adat.get("alma_pontszam", 0) or 0)
            oles = int(adat.get("olesek", 0) or 0)
            hossz = int(adat.get("hoszusag", 0) or 0)
            datum = self.ranglista_datum_szoveg(adat)

            sor = (
                f"{index + 1:<5} "
                f"{nev:<18} "
                f"{mode:<8} "
                f"{nehezseg:<12} "
                f"{ido:>7.1f} mp   "
                f"{pont:>5}   "
                f"{oles:>4}   "
                f"{hossz:>5}   "
                f"{datum}"
            )

            szin = (230, 230, 230)
            if index == 0:
                szin = (255, 215, 80)
            elif index == 1:
                szin = (210, 210, 210)
            elif index == 2:
                szin = (210, 150, 80)

            sor_kep = self.font_mini.render(sor, True, szin)
            self.screen.blit(sor_kep, (40, y))
            y += sor_magassag

        also = self.font_mini.render(f"Találatok: {len(self.ranglista_adatok)}    Mutatva: {start + 1}-{vege}", True, (160, 160, 160))
        self.screen.blit(also, (40, self.magassag - 35))

    def ranglista_kovetkezo_ertek(self, aktualis, lehetosegek):
        if aktualis not in lehetosegek:
            return lehetosegek[0]

        index = lehetosegek.index(aktualis)
        index += 1

        if index >= len(lehetosegek):
            index = 0

        return lehetosegek[index]

    def ranglistak_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self._atmeretezes(event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.statusz = "home"
                    self.ranglista_nev_aktiv = False

                elif self.ranglista_nev_aktiv:
                    if event.key == pygame.K_RETURN:
                        self.ranglista_nev_aktiv = False
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    elif event.key == pygame.K_BACKSPACE:
                        self.ranglista_nev_szuro = self.ranglista_nev_szuro[:-1]
                        if self.ranglista_nev_szuro.strip() == "":
                            self.ranglista_nev_szuro = "all"
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    elif event.unicode.isprintable():
                        if self.ranglista_nev_szuro == "all":
                            self.ranglista_nev_szuro = ""

                        if len(self.ranglista_nev_szuro) < 80:
                            self.ranglista_nev_szuro += event.unicode
                            self.ranglista_scroll = 0
                            self.ranglista_frissitese()

            elif event.type == pygame.MOUSEWHEEL:
                self.ranglista_scroll -= event.y
                self.ranglista_frissitese()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.ranglista_scroll -= 1
                    self.ranglista_frissitese()

                elif event.button == 5:
                    self.ranglista_scroll += 1
                    self.ranglista_frissitese()

                elif event.button == 1:
                    pos = event.pos

                    if self.ranglista_vissza_rect and self.ranglista_vissza_rect.collidepoint(pos):
                        self.statusz = "home"
                        self.ranglista_nev_aktiv = False

                    elif self.ranglista_mode_rect and self.ranglista_mode_rect.collidepoint(pos):
                        self.ranglista_mode_szuro = self.ranglista_kovetkezo_ertek(self.ranglista_mode_szuro, ["all", "alma", "tankos"])
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    elif self.ranglista_nehezseg_rect and self.ranglista_nehezseg_rect.collidepoint(pos):
                        self.ranglista_nehezseg_szuro = self.ranglista_kovetkezo_ertek(self.ranglista_nehezseg_szuro, ["all", "Easy", "Normal", "Hard", "Nightmare", "Hell"])
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    elif self.ranglista_nev_rect and self.ranglista_nev_rect.collidepoint(pos):
                        self.ranglista_nev_aktiv = True

                    elif self.ranglista_rendezes_rect and self.ranglista_rendezes_rect.collidepoint(pos):
                        self.ranglista_rendezes = self.ranglista_kovetkezo_ertek(self.ranglista_rendezes, ["datum", "tulelesiido", "pontszam", "olesek", "hosszusag"])
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    elif self.ranglista_irany_rect and self.ranglista_irany_rect.collidepoint(pos):
                        self.ranglista_csokkeno = not self.ranglista_csokkeno
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    elif self.ranglista_frissites_rect and self.ranglista_frissites_rect.collidepoint(pos):
                        self.ranglista_scroll = 0
                        self.ranglista_frissitese()

                    else:
                        self.ranglista_nev_aktiv = False


    def _platformer_assets_brtoltes(self):
        self.platformer_kepek_ut = os.path.join(os.path.dirname(__file__), "tiles", "platformer")
        self.platformer_babuk = {}
        self.eltolodott_kamera_x = self.kamera_x
        self.eltolodott_kamera_y = self.kamera_y
        self.the_assets_are_loading()
        self.jatekos = P_eloleny("?", golem=self.golem)
        

    def _fo_menu_vissza(self):
        if self.halozat:
            self.halozat.leallit()
            self.halozat = None
        self.helyi_vilag = None
        self.utolso_allapot = None
        self.statusz = "home"
        self.paused = False
        self.halal_allapot = None

    def _home_rajzolas(self):
        self.screen.fill((15, 15, 70))
        self._szin_frissites()
        
        self.settings_szoveg_rect = pygame.Rect(self.szeleseg -120, 15, 100, 25)
        pygame.draw.rect(self.screen, (25, 25, 25), self.settings_szoveg_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 255, 0) if self.settings_szoveg_rect else (80, 80, 80), self.settings_szoveg_rect, 2, border_radius=10)

        szoveg_0 = self.font_kis.render("Settings", True, (255, 255, 255))
        self.screen.blit(szoveg_0, (self.szeleseg -100, 20))

        ad_meg_neved = self.font_kozep.render("Add meg a nevedet:", True, (255, 255, 255))
        self.screen.blit(ad_meg_neved, (self.szeleseg // 2 - 250, 130))

        self.nev_szoveg_rect = pygame.Rect(self.szeleseg // 2 - 40, 120, 320, 42)
        pygame.draw.rect(self.screen, (255, 255, 255), self.nev_szoveg_rect, border_radius=15)
        pygame.draw.rect(self.screen, (0, 255, 0) if self.aktiv_nev_szovegdoboz else (80, 80, 80), self.nev_szoveg_rect, 2, border_radius=15)
        nev_szoveg = self.font_kozep.render(self.nev, True, (20, 20, 20))
        self.screen.blit(nev_szoveg, (self.nev_szoveg_rect.x + 6, self.nev_szoveg_rect.y + 10))

        for index, kulcs in enumerate(self.jatek_mode_valasztas):
            szin = (255, 0, 0) if kulcs == "alma" else (255, 255, 0)
            gomb_rect = pygame.Rect(self.szeleseg // 2 - 220 + index * 240, 190, 210, 54)
            self.jatek_mode_valasztas[kulcs]["rect"] = gomb_rect
            pygame.draw.rect(self.screen, szin, gomb_rect, border_radius=15)
            if kulcs == self.jatek_mode:
                pygame.draw.rect(self.screen, (0, 0, 0), gomb_rect, 3, border_radius=15)
            felirat = self.font_kozep.render(kulcs, True, (0, 0, 0))
            self.screen.blit(felirat, (gomb_rect.x + 60, gomb_rect.y + 13))

        for index, kulcs in enumerate(self.neheyseg_gombok):
            szin = (100, 255, 100) if kulcs == "Easy" else (255, 255, 100) if kulcs == "Normal" else (255, 150, 0) if kulcs == "Hard" else (255, 50, 50) if kulcs == "Nightmare" else (150, 0, 0)
            gomb_rect = pygame.Rect(self.szeleseg // 2 - 100, 280 + index * 56, 200, 46)
            self.neheyseg_gombok[kulcs]["rect"] = gomb_rect
            pygame.draw.rect(self.screen, szin, gomb_rect, border_radius=15)
            if kulcs == self.nehezseg_szint:
                pygame.draw.rect(self.screen, (0, 0, 0), gomb_rect, 3, border_radius=15)
            felirat = self.font_kis.render(kulcs, True, (0, 0, 0))
            self.screen.blit(felirat, (gomb_rect.x + 60, gomb_rect.y + 12))
        if self.jatek_mode != "platformer":
            szin_cim = self.font_kis.render("Player color settings:", True, (0, 255, 0))
            self.screen.blit(szin_cim, (self.szeleseg // 2 - szin_cim.get_width() // 2, 0))
            pygame.draw.circle(self.screen, self.szin, (self.szeleseg // 2, 55), 20)
            for index, kulcs in enumerate(self.szin_beallitasok):
                adat = self.szin_beallitasok[kulcs]
                adat["rect"] = pygame.Rect(self.szeleseg // 2 - 120 + index * 80, 80, 60, 30)
                pygame.draw.rect(self.screen, (180, 180, 180) if adat["aktiv"] else (255, 255, 255), adat["rect"], border_radius=15)
                pygame.draw.rect(self.screen, (0, 255, 0) if adat["aktiv"] else (70, 70, 70), adat["rect"], 2, border_radius=15)
                ertek = self.font_kis.render(adat["ertek"], True, (20, 20, 20))
                self.screen.blit(ertek, (adat["rect"].x + 15, adat["rect"].y + 10))

        
        for sorszam, (kulcs, adat) in enumerate(self.inditasi_gombok.items()):
            gomb_rect = pygame.Rect(self.szeleseg // 2 - 360 + sorszam * 240, 610, 220, 54)
            adat["rect"] = gomb_rect
            szin = (0, 200, 0) if kulcs == "single" else (0, 170, 255) if kulcs == "create" else (255, 140, 0)
            pygame.draw.rect(self.screen, szin, gomb_rect, border_radius=15)
            felirat = self.font_kis.render(adat["felirat"], True, (0, 0, 0))
            self.screen.blit(felirat, (gomb_rect.x + 62, gomb_rect.y + 15))
            

        kod_label = self.font_kis.render("Room code:", True, (255, 255, 255))
        self.screen.blit(kod_label, (self.szeleseg // 2 - 150, 570))
        self.szoba_kod_rect = pygame.Rect(self.szeleseg // 2 - 50, 560, 140, 36)
        pygame.draw.rect(self.screen, (255, 255, 255), self.szoba_kod_rect, border_radius=15)
        pygame.draw.rect(self.screen, (0, 255, 0) if self.szoba_kod_aktiv else (80, 80, 80), self.szoba_kod_rect, 2, border_radius=15)
        kod = self.font_kis.render(self.szoba_kod, True, (20, 20, 20))
        self.screen.blit(kod, (self.szoba_kod_rect.x + 6, self.szoba_kod_rect.y + 10))

        szerver_info = self.font_kis.render(f"Központi szerver: {KOZPONTI_SZERVER_CIM}", True, (160, 160, 160))
        self.screen.blit(szerver_info, (self.szeleseg // 2 - szerver_info.get_width() // 2, 700))

        if self.home_hiba:
            hiba = self.font_kis.render(self.home_hiba, True, (255, 120, 120))
            self.screen.blit(hiba, (self.szeleseg // 2 - hiba.get_width() // 2, 730))

        self.ranglistak_rect = pygame.Rect(self.szeleseg - 240, self.magassag- 70, 220, 50)
        pygame.draw.rect(self.screen, (245, 50, 80),self.ranglistak_rect, border_radius=15)
        ranglista = self.font_kis.render("RANGLISTÁK", True, (20, 20, 20))
        self.screen.blit(ranglista, (self.ranglistak_rect.x + 6, self.ranglistak_rect.y + 5))

        if self.jatek_mode == "tankos":
            tank_cim = self.font_kis.render("Tank választás:", True, (0, 255, 0))
            self.screen.blit(tank_cim, (40, 120))
            self.tank.tankok_meretezese_szinezese(50, self.szin)

            for index, tank_nev in enumerate(self.tank_valaszto_gombok):
                rect = pygame.Rect(40, 155 + index * 52, 140, 42)
                
                self.tank_valaszto_gombok[tank_nev]["rect"] = rect  
                
                
                szin = (80, 220, 80) if self.tank.tank == tank_nev else (180, 180, 180)
                
                szin = (80, 220, 80) if self.golem == tank_nev else (180, 180, 180)

                pygame.draw.rect(self.screen, szin, rect, border_radius=15)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2, border_radius=15)
                
                self.tank.tank_rajzolas(self.screen, rect.x + rect.w // 2 - felirat.get_width() // 2, rect.y + rect.h // 2 - felirat.get_height() // 2, melyik=tank_nev)
               


        if self.jatek_mode == "platformer":
            tank_cim = self.font_kis.render("Golem választás", True, (0, 255, 0))
            self.screen.blit(tank_cim, (40, 130))

            for index, tank_nev in enumerate(self.tank_valaszto_gombok if self.jatek_mode =="tankos" else self.golem_valaszto_gombok.keys()):
                
                rect = pygame.Rect(50,  150 + index * (self.picture_of_golems[index].get_height() + 40), self.picture_of_golems[index].get_width()+20, self.picture_of_golems[index].get_height()+20)
                self.golem_valaszto_gombok[tank_nev]["rect"] = rect
                szin = (80, 220, 80) if self.golem == str(int(tank_nev)+1) else (180, 180, 180)

                pygame.draw.rect(self.screen, szin, rect, border_radius=15)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2, border_radius=15)
                self.screen.blit(self.picture_of_golems[int(tank_nev)], (rect.x + 10, rect.y + 10))





            for index, kulcs in enumerate(self.vilag_bealitas):
                adat = self.vilag_bealitas[kulcs]
                szoveg = self.font_kis.render(adat["szoveg"], True, (255, 255, 255))
                self.screen.blit(szoveg, (self.szeleseg // 2 - 120  + 230, 300 + index * 30))
                adat["rect"] = pygame.Rect(self.szeleseg // 2 - 120  + 400, 300 + index * 30, 60, 30)
                pygame.draw.rect(self.screen, (180, 180, 180) if adat["aktiv"] else (255, 255, 255), adat["rect"], border_radius=15)
                pygame.draw.rect(self.screen, (0, 255, 0) if adat["aktiv"] else (70, 70, 70), adat["rect"], 2, border_radius=15)
                ertek = self.font_kis.render(adat["ertek"], True, (200, 20, 20))
                self.screen.blit(ertek, (adat["rect"].x + 4, adat["rect"].y + 2))
        
        mobil_szoveg = "Mód: Mobil" if self.is_mobile else "Mód: PC (Gép)"
        gomb_szin = (0, 200, 100) if self.is_mobile else (120, 120, 120)
        pygame.draw.rect(self.screen, gomb_szin, self.mobil_valaszto_rect, border_radius=15)
        pygame.draw.rect(self.screen, (230, 230, 230), self.mobil_valaszto_rect, 2, border_radius=15)
        felirat = self.font_kis.render(mobil_szoveg, True, (255, 255, 255))
        self.screen.blit(felirat, (self.mobil_valaszto_rect.x + 10, self.mobil_valaszto_rect.y + 10))

    def _home_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.settings_mentes()
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self._atmeretezes(event.w, event.h)
                self.settings_mentes()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.nev_szoveg_rect and self.nev_szoveg_rect.collidepoint(event.pos):
                    self.aktiv_nev_szovegdoboz = True
                    for masik in self.szin_beallitasok.values():
                        masik["aktiv"] = False
                    for masik in self.vilag_bealitas.values():
                        masik["aktiv"] = False
                    if self.is_mobile:
                            pygame.key.start_text_input()
                    self.szoba_kod_aktiv = False
                elif self.szoba_kod_rect and self.szoba_kod_rect.collidepoint(event.pos):
                    self.szoba_kod_aktiv = True
                    self.aktiv_nev_szovegdoboz = False
                    for masik in self.szin_beallitasok.values():
                        masik["aktiv"] = False
                    for masik in self.vilag_bealitas.values():
                        masik["aktiv"] = False
                    if self.is_mobile:
                            pygame.key.start_text_input()
                elif self.ranglistak_rect and self.ranglistak_rect.collidepoint(event.pos):
                    self.ranglistak_betoltese()
                elif self.mobil_valaszto_rect.collidepoint(event.pos):
                    self._mobil_mod_be_ki()
                elif self.settings_szoveg_rect and self.settings_szoveg_rect.collidepoint(event.pos):
                    self.elozo_statusz = "home"
                    self.statusz = "settings"
                else:
                    self.aktiv_nev_szovegdoboz = False
                    self.szoba_kod_aktiv = False

                for tank_nev, adat in self.tank_valaszto_gombok.items():
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        self.tank.tank_valasztas(tank_nev)
                        self.tank.tankok_meretezese_szinezese(60, self.szin)
                        
                        break
                for golem_nev, adat in self.golem_valaszto_gombok.items():
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        self.golem = str(int(golem_nev)+1)
                        print(self.golem)
                        break
                for kulcs, adat in self.jatek_mode_valasztas.items():
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        self.jatek_mode = kulcs
                        break
                for kulcs, adat in self.neheyseg_gombok.items():
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        self.nehezseg_szint = kulcs
                        self.vilag_bealitas["AI_db"]["ertek"] = str(self.beallitasok.nehezseg_atvalto[self.nehezseg_szint])
                        break
                for kulcs, adat in self.inditasi_gombok.items():
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        if not (self.nev.strip() or kulcs != "single"):
                            pass
                        if self.jatek_mode == "tankos":
                            self._szin_frissites()
                            self.tank.tankok_meretezese_szinezese(60, self.szin)
                            self.buffok = Buff()
                        if kulcs == "single":
                            self._single_inditas()
                        else:
                            self._multiplayer_inditas(kulcs)
                        break
                for kulcs in self.szin_beallitasok:
                    adat = self.szin_beallitasok[kulcs]
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        for masik in self.szin_beallitasok.values():
                            masik["aktiv"] = False
                        for masik in self.vilag_bealitas.values():
                            masik["aktiv"] = False
                        self.aktiv_nev_szovegdoboz = False
                        self.szoba_kod_aktiv = False
                        if self.is_mobile:
                            pygame.key.start_text_input()
                        adat["aktiv"] = True
                        break
                
                for kulcs in self.vilag_bealitas:
                    adat = self.vilag_bealitas[kulcs]
                    if adat["rect"] and adat["rect"].collidepoint(event.pos):
                        for masik in self.vilag_bealitas.values():
                            masik["aktiv"] = False
                        for masik in self.szin_beallitasok.values():
                            masik["aktiv"] = False
                        self.aktiv_nev_szovegdoboz = False
                        self.szoba_kod_aktiv = False
                        if self.is_mobile:
                            pygame.key.start_text_input()
                        adat["aktiv"] = True
                        break
                self.settings_mentes()
            elif event.type == pygame.KEYDOWN:
                if self.aktiv_nev_szovegdoboz:
                    if event.key == pygame.K_BACKSPACE:
                        self.nev = self.nev[:-1]
                    elif event.unicode.isprintable() and len(self.nev) < 20:
                        self.nev += event.unicode
                elif self.szoba_kod_aktiv:
                    if event.key == pygame.K_BACKSPACE:
                        self.szoba_kod = self.szoba_kod[:-1]
                    elif event.unicode.isdigit() and len(self.szoba_kod) < self.beallitasok.szoba_kod_hossz:
                        self.szoba_kod += event.unicode
                else:
                    for adat in self.szin_beallitasok.values():
                        if adat["aktiv"]:
                            if event.key == pygame.K_BACKSPACE:
                                adat["ertek"] = adat["ertek"][:-1]
                            elif event.unicode.isdigit() and len(adat["ertek"]) < 3:
                                proba = self._szamot_ertekre(adat["ertek"] + event.unicode)
                                if 0 <= proba <= 255:
                                    adat["ertek"] += event.unicode

                    for adat in self.vilag_bealitas.values():
                        if adat["aktiv"]:
                            if event.key == pygame.K_BACKSPACE:
                                adat["ertek"] = adat["ertek"][:-1]
                            elif event.unicode.isdigit() and len(adat["ertek"]) < 5:
                                proba = self._szamot_ertekre(adat["ertek"] + event.unicode)
                                if proba:
                                    adat["ertek"] += event.unicode
                self._szin_frissites()
                self.settings_mentes()
    
    def _varakozas_rajzolas(self):
        self.screen.fill((0, 0, 0))
        cim = self.font_nagy.render("Kapcsolódás a központi szerverhez...", True, (0, 255, 0))
        self.screen.blit(cim, (self.szeleseg // 2 - cim.get_width() // 2, self.magassag // 2 - 80))
        szoveg = self.font_kis.render(self.varakozas_szoveg, True, (220, 220, 220))
        self.screen.blit(szoveg, (self.szeleseg // 2 - szoveg.get_width() // 2, self.magassag // 2))
        if self.halozati_mod == "create" and self.szoba_kod:
            kod = self.font_kozep.render(f"Szobakód: {self.szoba_kod}", True, (255, 220, 0))
            self.screen.blit(kod, (self.szeleseg // 2 - kod.get_width() // 2, self.magassag // 2 + 48))
        #pygame.display.update()

    def _varakozas_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self._atmeretezes(event.w, event.h)

        if self.halozat is None:
            return
        if self.halozat.init_megkapva and self.halozat.sajat_id:
            self.szoba_kod = self.halozat.szoba_kod
            self.jatek_mode = self.halozat.jatek_mode
            self.nehezseg_szint = self.halozat.nehezseg_szint
            self.statusz = "jatek"
            self.varakozas_szoveg = "Kapcsolódva!"
            return
        if self.halozat.hiba:
            self.home_hiba = f"Kapcsolati hiba: {self.halozat.hiba}"
            self._fo_menu_vissza()

    def _atmeretezes(self, uj_szelesseg: int, uj_magassag: int):
        self.szeleseg = uj_szelesseg
        self.magassag = uj_magassag
        if self.halozat:
            self.halozat.kuldd({"tipus": "atmeretezes", "szelesseg": self.szeleseg, "magassag": self.magassag})

    def _lokalis_input_frissites(self):
        if self.helyi_vilag is None:
            return
        
        if self.is_mobile:
            fel = self.joystick_irany_y < -0.3
            le = self.joystick_irany_y > 0.3
            bal = self.joystick_irany_x < -0.3
            jobb = self.joystick_irany_x > 0.3
            loves = self.mobil_loves
            
            
            if self.halozati_mod == "single":
                if self.helyi_vilag:
                    self.helyi_vilag.mozgas_beallitas(self.helyi_jatekos_id, bal, jobb, fel, le, loves)
            else:
                if bal != self.bal or jobb != self.jobb or fel != self.fel or le != self.le or loves != self.mobil_loves:
                    self.halozat.kuldd({"tipus": "mozgas", "balra": bal, "jobbra": jobb, "fel": fel,"le": le, "loves": loves})
            self.fel, self.jobb, self.le, self.bal = fel, jobb, le, bal
            return


        if self.jatek_mode == "alma":
            allapot = self.helyi_vilag.nezet_jatekosnak(self.helyi_jatekos_id, self.szeleseg, self.magassag)
            sajat = allapot["jatekosok"].get(self.helyi_jatekos_id)
            if sajat and sajat["el"] and sajat["test_pontok"]:
                fej_x, fej_y = sajat["test_pontok"][0]
                eger_x, eger_y = pygame.mouse.get_pos()
                cel_x = eger_x + allapot["kamera_x"]
                cel_y = eger_y + allapot["kamera_y"]
                dx = cel_x - fej_x
                dy = cel_y - fej_y
                self.helyi_vilag.jatekos_irany_beallitasa(self.helyi_jatekos_id, dx, dy)
                self.helyi_vilag.jatekos_gyorsitas_beallitasa(self.helyi_jatekos_id, bool(pygame.mouse.get_pressed()[0]))
        else:
            lista = ["space", "left", "up", "down", "right"]
            gombok = pygame.key.get_pressed()
            self.helyi_vilag.mozgas_beallitas(
                self.helyi_jatekos_id,
                gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("left").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("left") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("left"))],
                gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("right").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("right") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("right"))],
                gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("up").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("up") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("up"))],
                gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("down").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("down") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("down"))],
                gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("bumm").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("bumm") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("bumm"))],
            )

    def _halozati_input_frissites(self):
        if not self.halozat or not self.utolso_allapot:
            return
        
        if self.is_mobile:
            fel = self.joystick_irany_y < -0.3
            le = self.joystick_irany_y > 0.3
            bal = self.joystick_irany_x < -0.3
            jobb = self.joystick_irany_x > 0.3
            loves = self.mobil_loves
            
            
            if self.halozati_mod == "single":
                if self.helyi_vilag:
                    self.helyi_vilag.jatekos_iranyitas_beallitas(self.helyi_jatekos_id, bal, jobb, fel, le, loves)
            else:
                if bal != self.bal or jobb != self.jobb or fel != self.fel or le != self.le or loves != self.mobil_loves:
                    self.halozat.kuldd({"tipus": "mozgas", "balra": bal, "jobbra": jobb, "fel": fel, "le": le, "loves": loves})
            self.fel, self.jobb, self.le, self.bal = fel, jobb, le, bal
            return

        if self.jatek_mode == "alma":
            sajat = self.utolso_allapot["jatekosok"].get(self.halozat.sajat_id)

            test_pontok = sajat.get("test_pontok", []) if sajat else []

            if sajat and sajat.get("el", True) and test_pontok:
                fej_x, fej_y = test_pontok[0]

                eger_x, eger_y = pygame.mouse.get_pos()
                cel_x = eger_x + self.utolso_allapot["kamera_x"]
                cel_y = eger_y + self.utolso_allapot["kamera_y"]

                dx = cel_x - fej_x
                dy = cel_y - fej_y
                hossz = math.hypot(dx, dy)

                if hossz > 1e-6:
                    dx /= hossz
                    dy /= hossz
                    
                    if abs(dx - self.volt_irany_x) > 0.01 or abs(dy - self.volt_irany_y) > 0.01:
                        self.halozat.kuldd({"tipus": "irany", "dx": dx, "dy": dy})

                        self.volt_irany_x = dx
                        self.volt_irany_y = dy

                gyors = bool(pygame.mouse.get_pressed()[0])

                if gyors != self.volt_gyors:
                    self.halozat.kuldd({"tipus": "sebesseg", "gyors": gyors})
                    self.volt_gyors = gyors

        else:
            lista = ["space", "left", "up", "down", "right"]
            gombok = pygame.key.get_pressed()
            bal = gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("left").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("left") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("left"))]
            jobb = gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("right").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("right") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("right"))]
            fel = gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("up").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("up") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("up"))]
            le = gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("down").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("down") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("down"))]
            loves = gombok[getattr(pygame, "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("bumm").upper() if self.billentyu_kiosztas.get(self.jatek_mode).get("bumm") in lista else "K_" + self.billentyu_kiosztas.get(self.jatek_mode).get("bumm"))]
            
            if bal != self.bal or jobb != self.jobb or fel != self.fel or le != self.le or loves != self.halozat_volt_loves:
                self.halozat.kuldd({"tipus": "mozgas", "balra": bal, "jobbra": jobb, "fel": fel, "le": le, "loves": loves})
                self.fel = fel
                self.jobb = jobb
                self.le = le
                self.bal = bal
                self.halozat_volt_loves = loves

    def _frissits_allapotot(self, delta_ido):
        if self.halozati_mod == "single":
            self._lokalis_input_frissites()
            if not self.paused:
                self.helyi_vilag.frissites(delta_ido)
            self.utolso_allapot = self.helyi_vilag.nezet_jatekosnak(self.helyi_jatekos_id, self.szeleseg, self.magassag)
        else:
            self._halozati_input_frissites()
            if self.halozat:
                uj = self.halozat.legfrissebb_allapot()
                if uj is not None:
                    if uj.get("tipus") == "nagy":
                        self.utolso_allapot = uj
                        self.regi = copy.deepcopy(uj)
                        
                    elif uj.get("tipus") == "kicsi":
                        if not self.regi:
                            return
                        self.utolso_allapot = self.kliens_seged_vilag.kicsi_csomag_mozgatas(uj, self.regi, self.szeleseg, self.magassag)
                        self.regi = copy.deepcopy(self.utolso_allapot)
                        
        if self.utolso_allapot:
            self.kamera_x = self.utolso_allapot.get("kamera_x", 0.0)
            self.kamera_y = self.utolso_allapot.get("kamera_y", 0.0)

            sajat_id = self.helyi_jatekos_id if self.halozati_mod == "single" else self.halozat.sajat_id
            sajat = self.utolso_allapot.get("jatekosok", {}).get(sajat_id)
            

            if sajat is None:
                if self.statusz != "halott":
                    self.halal_allapot = copy.deepcopy(self.utolso_allapot)
                self.statusz = "halott"
                
            elif not sajat.get("el", True):
                if self.statusz != "halott":
                    self.halal_allapot = copy.deepcopy(self.utolso_allapot)
                self.statusz = "halott"





    def _jatek_rajzolas(self, delta_ido):
        lott = False
        self.screen.fill((0, 0, 0))
        if self.jatek_mode == "platformer":
            self.screen.fill((80, 80, 106))
        rajzolt_allapot = self.halal_allapot if self.statusz == "halott" and self.halal_allapot else self.utolso_allapot
        if not rajzolt_allapot:
            return
        #if self.statusz != "halott":
        if not rajzolt_allapot:
            #pygame.display.update()
            return

        #pygame.draw.rect(self.screen, (255, 255, 255), (0 - self.kamera_x - 5, 0 - self.kamera_y - 5, rajzolt_allapot["vilag_szelesseg"], rajzolt_allapot["vilag_magassag"]), 5,)

        if rajzolt_allapot["jatek_mode"] == "alma":
            for alma_x, alma_y in rajzolt_allapot.get("almak", []):
                pygame.draw.circle(self.screen, (255, 100, 100), (int(alma_x - self.kamera_x), int(alma_y - self.kamera_y)), int(self.beallitasok.alma_kor_sugár))

            sajat_id = self.helyi_jatekos_id if self.halozati_mod == "single" else self.halozat.sajat_id

            for kigyo in list(rajzolt_allapot.get("kigyo_ellenseg", [])) + list(rajzolt_allapot.get("jatekosok", {}).values()):
                if self.statusz == "halott" and kigyo.get("azonosito") == sajat_id:
                    continue
                self._kigyo_rajzolas(kigyo)

            sajat_id = self.helyi_jatekos_id if self.halozati_mod == "single" else self.halozat.sajat_id
            sajat = rajzolt_allapot.get("jatekosok", {}).get(sajat_id)

            if sajat and sajat.get("test_pontok"):
                self.fej_x, self.fej_y = sajat["test_pontok"][0]
                self.koordinata_szoveg = f"{round(self.fej_x), round(self.fej_y)}"
                self.pontszam = sajat.get("pontok", 0)
                self.testhossz = sajat.get("ossz_testhosz", 0)
                self.olesek = sajat.get("olesek", 0)
                self.ido = sajat.get("eltelt_ido", 0)
            
            hud = self.font_kis.render(
                f"eltelt idő: {round(self.ido)}    pontszám: {self.pontszam}    testhosz: {self.testhossz}    ölések: {self.olesek}    játékosok: {len(rajzolt_allapot.get('jatekosok', {}))}    kordinata: {self.koordinata_szoveg}    {'kod: ' + self.halozat.szoba_kod if self.halozat else ''}  ", 
                True, (255, 255, 255),)
            self.screen.blit(hud, (self.pause_gomb.x if self.halozat else 220, 18))
        elif rajzolt_allapot["jatek_mode"] == "tankos":
            sajat_id = self.helyi_jatekos_id if self.halozati_mod == "single" else self.halozat.sajat_id
            sajat = rajzolt_allapot.get("jatekosok", {}).get(sajat_id)

            self._tankos_terkep_rajzolas(rajzolt_allapot)

            aktualis_azonositok = set(rajzolt_allapot.get("jatekosok", {}).keys())
            for chast in rajzolt_allapot.get("buff", {}):
                self.buffok.buff_rajzolas(self.screen, chast.get("kincs_fajta", "hp"), chast.get("x"), chast.get("y"), self.kamera_x, self.kamera_y)
            

            for regi_id in list(self.ellenseg_tankok.keys()):
                if regi_id not in aktualis_azonositok:
                    del self.ellenseg_tankok[regi_id]

            for jatekos_id, jatekos in rajzolt_allapot.get("jatekosok", {}).items():
                if not jatekos["el"]:
                    continue
                tank_tipus = jatekos.get("kep") or "tank_1_kek"
                szin = tuple(jatekos.get("szin", (200, 200, 200)))
                if not lott and jatekos.get("tuzelt"):
                    lott = True
                    self.hangok["sima_tank_loves"].set_volume(self.mousick_settings["tank_loves"])
                    self.hangok["sima_tank_loves"].play()

                kulcs = (jatekos_id, tank_tipus, szin)

                if jatekos_id not in self.ellenseg_tankok:
                    kep = self.tank.eredeti_kepek[tank_tipus].copy()
                    kep = pygame.transform.scale(kep, (60, int(kep.get_height() * (60 / kep.get_width()))))
                    self.ellenseg_tankok[jatekos_id] = Kepernyo_tank(kep, szin)

                self.ellenseg_tankok[jatekos_id].tank_rajzolas(
                    self.screen,
                    int(jatekos["x"]),
                    int(jatekos["y"]),
                    self.kamera_x,
                    self.kamera_y,
                    jatekos.get("fok", 0)
                )

            for lovedek in rajzolt_allapot.get("lovedekek", []):
                pygame.draw.circle(self.screen,(0, 0, 0),(int(lovedek["x"] - self.kamera_x),int(lovedek["y"] - self.kamera_y)),int(lovedek["sugar"]))

            
            if sajat:
                self.fej_x = sajat.get("x", 0)
                self.fej_y = sajat.get("y", 0)
                self.koordinata_szoveg = f"{round(self.fej_x), round(self.fej_y)}"

                self.pontszam = sajat.get("pontok", 0)
                self.olesek = sajat.get("olesek", 0)
                self.ido = sajat.get("eltelt_ido", 0)
                self.hp = sajat.get("hp", 0)
                    
                
                self._tankos_felso_hud_rajzolas(sajat, len(rajzolt_allapot.get("jatekosok", {})))

                self._aktiv_buff_sav_rajzolas(sajat.get("buffok", []))

                if sajat.get("uj_buffok", {}) != {}:
                    for nev in sajat.get("uj_buffok"):
                        i = sajat.get("uj_buffok")[nev]
                        self.uj_buffok[nev] = i


                if self.uj_buffok != {}:
                    for index, nev in enumerate(self.uj_buffok):
                        adatok = self.uj_buffok[nev]
                        szoveg = f"{nev[:-1] if nev != "teleport" else nev} {nev[-1] if nev != "teleport" else " "} "\
                            f"{adatok[1] if nev != "teleport" else " "} {"for" if nev[:-1] != "hp" else ""} {adatok[2] if nev[:-1] != "hp" else ""} {"s" if nev[:-1] != "hp" else ""}" if nev != "teleport" else "teleport"
                        index += 1
                        terfel = "p" if nev[-1] == "+" else "n" if nev[-1] == "-" else "s"
                        szoveg = self.font_kozep.render(szoveg, True, (0, 230, 0) if  terfel == "p" else (230, 0, 0) if terfel == "n" else (255, 255, 255))
                        x = self.fej_x - self.kamera_x - szoveg.get_width()//2 
                        y = self.fej_y - self.kamera_y - 50 * index 

                        self.screen.blit(szoveg, (x, y))
                        self.uj_buffok[nev][0] = self.uj_buffok[nev][0] - delta_ido
                        if self.uj_buffok[nev][0] <= 0:
                            self.uj_buffok_torlese.append(nev)
                    for i in self.uj_buffok_torlese:
                        del self.uj_buffok[i]
                    self.uj_buffok_torlese = []
        elif rajzolt_allapot["jatek_mode"] == "platformer":



            
            zoom = self.platformer_zoom

            rajz_kamera_x = self.kamera_x + self.screen.get_width() / 2 - self.screen.get_width() / (2 * zoom)
            rajz_kamera_y = self.kamera_y + self.screen.get_height() / 2 - self.screen.get_height() / (2 * zoom)

            for reteg in self.platformer_terkep["rajz_retegek"]:
                meret = reteg["tile_meret"]

                bal_cella = math.floor(rajz_kamera_x / meret) - 1
                jobb_cella = math.floor((rajz_kamera_x + self.screen.get_width() / zoom) / meret) + 1
                felso_cella = math.floor(rajz_kamera_y / meret) - 1
                also_cella = math.floor((rajz_kamera_y + self.screen.get_height() / zoom) / meret) + 1

                for cella_y in range(felso_cella, also_cella + 1):
                    for cella_x in range(bal_cella, jobb_cella + 1):
                        for tile in reteg["rajz_racs"].get((cella_x, cella_y), ()):
                            screen_x = int((tile["x"] - rajz_kamera_x) * zoom)
                            screen_y = int((tile["y"] - rajz_kamera_y) * zoom)
                            self.screen.blit(tile["kep"], (screen_x, screen_y))
            



            if rajzolt_allapot["szoba"] != self.jelenlegi_szoba:
                self.jelenlegi_szoba = rajzolt_allapot["szoba"]

            for jatekos_id, jatekos in rajzolt_allapot.get("jatekosok", {}).items():
                self.kamera_mozgatasa(jatekos.get("x"), jatekos.get("y"))
                rect = pygame.Rect(jatekos.get("x") - self.kamera_x, jatekos.get("y") - self.kamera_y, self.jatekos.kepek["Idle"][0].get_width(), self.jatekos.kepek["Idle"][0].get_height())
                akciok = jatekos.get("akcio")
                irany = jatekos.get("irany")
                if "Idle" == akciok or irany == 0:
                    akcio = "Idle"
                elif irany == 1:
                    akcio = "Running"
                else:
                    akcio = "Running"

                if "Falling Down" == akciok:
                    akcio = "Falling Down"
                elif "Jump Start" == akciok:
                    akcio = "Jump Start"

                

                jatekos_screen_x = (jatekos.get("x") - rajz_kamera_x) * zoom
                jatekos_screen_y = (jatekos.get("y") - rajz_kamera_y) * zoom
                self.jatekos.rajzolas(self.screen, jatekos_screen_x, jatekos_screen_y, 0, 0, melyik=akcio, forgatas=irany)
                # self.jatekos.rajzolas(self.screen, jatekos.get("x"), jatekos.get("y"), self.kamera_x, self.kamera_y, melyik=akcio, forgatas=irany)
                #pygame.draw.rect(self.screen, (255, 0, 0), rect)
            pass

        if not self.halozat and rajzolt_allapot["jatek_mode"] != "tankos":
            pygame.draw.rect(self.screen, (100, 255, 100), self.pause_gomb)
            pause_txt = self.font_kis.render("PAUSE", True, (0, 0, 0))
            self.screen.blit(pause_txt, (self.pause_gomb.centerx - pause_txt.get_width() // 2, self.pause_gomb.centery - pause_txt.get_height() // 2,))

        if self.paused and self.halozati_mod == "single":
            self._pause_rajzolas()


        if self.is_mobile:
            pygame.draw.circle(self.screen, (80, 80, 80), self.joystick_kozep, self.joystick_sugar, 4)
            
            kar_x = int(self.joystick_kozep[0] + self.joystick_irany_x * self.joystick_sugar)
            kar_y = int(self.joystick_kozep[1] + self.joystick_irany_y * self.joystick_sugar)
            pygame.draw.circle(self.screen, (150, 150, 150), (kar_x, kar_y), 25)
            
            
            gomb_szin = (220, 50, 50) if self.mobil_loves else (100, 100, 100)
            pygame.draw.circle(self.screen, gomb_szin, self.gomb_kozep, self.gomb_sugar)
            pygame.draw.circle(self.screen, (230, 230, 230), self.gomb_kozep, self.gomb_sugar, 3)
            
            loves_szoveg = self.font_kis.render("TŰZ", True, (255, 255, 255))
            self.screen.blit(loves_szoveg, (self.gomb_kozep[0] - loves_szoveg.get_width() // 2, self.gomb_kozep[1] - loves_szoveg.get_height() // 2))

    def settings_rajzolas(self):
        self.screen.fill((8, 11, 16))

        ful_magassag = 46
        ful_tavolsag = 12

        teljes_szelesseg = 0
        ful_adatok = []

        hatter = (24, 29, 37)
        szegely = (75, 87, 102)
        szoveg_szin = (175, 185, 195)
        felirat = self.font_kozep.render("vissza", True, szoveg_szin)
        self.settings_vissza = pygame.Rect(self.szeleseg-100, 30, felirat.get_width() + 10, felirat.get_height() + 5)

        pygame.draw.rect(self.screen, hatter, self.settings_vissza, border_radius=10)

        pygame.draw.rect(self.screen, szegely, self.settings_vissza, 2, border_radius=10)

        

        self.screen.blit(felirat,(self.settings_vissza.centerx - felirat.get_width() // 2, self.settings_vissza.centery - felirat.get_height() // 2,))

        

        for nev, adat in self.settings_oldalak.items():
            szoveg = self.font_kozep.render(nev, True, (255, 255, 255))
            ful_szelesseg = szoveg.get_width() + 42
            ful_adatok.append((nev, adat, szoveg, ful_szelesseg))
            teljes_szelesseg += ful_szelesseg

        teljes_szelesseg += max(0, len(ful_adatok) - 1) * ful_tavolsag

        x = self.szeleseg // 2 - teljes_szelesseg // 2
        y = 22

        for nev, adat, szoveg, ful_szelesseg in ful_adatok:
            adat["rect"] = pygame.Rect(x, y, ful_szelesseg, ful_magassag)

            if adat["klikd"]:
                hatter = (46, 112, 158)
                szegely = (115, 220, 255)
                szoveg_szin = (255, 255, 255)
            else:
                hatter = (24, 29, 37)
                szegely = (75, 87, 102)
                szoveg_szin = (175, 185, 195)

            pygame.draw.rect(self.screen, hatter, adat["rect"], border_radius=10)

            pygame.draw.rect(self.screen, szegely, adat["rect"], 2, border_radius=10)

            felirat = self.font_kozep.render(nev, True, szoveg_szin)

            self.screen.blit(felirat,(adat["rect"].centerx - felirat.get_width() // 2, adat["rect"].centery - felirat.get_height() // 2,))

            x += ful_szelesseg + ful_tavolsag


        aktiv_oldal = None

        for nev, adat in self.settings_oldalak.items():
            if adat["klikd"]:
                aktiv_oldal = nev
                break


        if aktiv_oldal == "Hangok":
            cim = self.font_nagy.render("HANGBEÁLLÍTÁSOK", True, (235, 240, 245))

            self.screen.blit(cim, (self.szeleseg // 2 - cim.get_width() // 2, 105))

            slider_adatok = [("Háttérzene", "backround_mousick", 225), ("Tank lövés", "tank_loves", 365),]

            slider_szelesseg = min(620, self.szeleseg - 160)

            slider_magassag = 16
            slider_x = self.szeleseg // 2 - slider_szelesseg // 2

            self.settings_slider_rectek = {}

            for felirat_szoveg, kulcs, slider_y in slider_adatok:
                try:
                    ertek = float(self.mousick_settings.get(kulcs, 0.5))
                except (TypeError, ValueError):
                    ertek = 0.5

                ertek = max(0.0, min(1.0, ertek))
                self.mousick_settings[kulcs] = ertek

                panel_rect = pygame.Rect(
                    slider_x - 40,
                    slider_y - 68,
                    slider_szelesseg + 80,
                    116
                )

                self._hud_panel(
                    panel_rect,
                    hatter=(14, 19, 27, 235),
                    szegely=(70, 93, 115, 230)
                )

                felirat = self.font_kozep.render(
                    felirat_szoveg,
                    True,
                    (230, 235, 240)
                )

                self.screen.blit(
                    felirat,
                    (
                        slider_x,
                        slider_y - 52
                    )
                )

                szazalek = self.font_kozep.render(
                    f"{round(ertek * 100)}%",
                    True,
                    (105, 220, 255)
                )

                self.screen.blit(
                    szazalek,
                    (
                        slider_x + slider_szelesseg - szazalek.get_width(),
                        slider_y - 52
                    )
                )

                slider_rect = pygame.Rect(
                    slider_x,
                    slider_y,
                    slider_szelesseg,
                    slider_magassag
                )

                self.settings_slider_rectek[kulcs] = slider_rect

                pygame.draw.rect(
                    self.screen,
                    (40, 47, 57),
                    slider_rect,
                    border_radius=slider_magassag // 2
                )

                kitoltes = pygame.Rect(
                    slider_rect.x,
                    slider_rect.y,
                    int(slider_rect.width * ertek),
                    slider_rect.height
                )

                if kitoltes.width > 0:
                    pygame.draw.rect(
                        self.screen,
                        (65, 178, 225),
                        kitoltes,
                        border_radius=slider_magassag // 2
                    )

                fogantyu_x = int(
                    slider_rect.x + slider_rect.width * ertek
                )

                pygame.draw.circle(
                    self.screen,
                    (235, 245, 250),
                    (
                        fogantyu_x,
                        slider_rect.centery
                    ),
                    13
                )

                pygame.draw.circle(
                    self.screen,
                    (65, 178, 225),
                    (
                        fogantyu_x,
                        slider_rect.centery
                    ),
                    13,
                    3
                )

                # 0, 25, 50, 75, 100 jelölések
                for jeloles in range(0, 101, 25):
                    jel_x = slider_rect.x + int(
                        slider_rect.width * jeloles / 100
                    )

                    pygame.draw.line(
                        self.screen,
                        (85, 95, 108),
                        (
                            jel_x,
                            slider_rect.bottom + 8
                        ),
                        (
                            jel_x,
                            slider_rect.bottom + 14
                        ),
                        2
                    )

                    jel_szoveg = self.font_mini.render(
                        str(jeloles),
                        True,
                        (135, 145, 158)
                    )

                    self.screen.blit(
                        jel_szoveg,
                        (
                            jel_x - jel_szoveg.get_width() // 2,
                            slider_rect.bottom + 18
                        )
                    )

            lepes_szoveg = self.font_kis.render(
                "A hangerő 5%-os lépésekben állítható.",
                True,
                (145, 155, 165)
            )

            self.screen.blit(
                lepes_szoveg,
                (
                    self.szeleseg // 2 - lepes_szoveg.get_width() // 2,
                    470
                )
            )

        elif aktiv_oldal == "Billentyű":
            ful_adatok = []
            teljes_szelesseg = 0
            for nev, adat in self.settings_billentyu_modok.items():
                szoveg = self.font_kis.render(nev, True, (255, 255, 255))
                ful_szelesseg = szoveg.get_width() + 40
                ful_adatok.append((nev, adat, szoveg, ful_szelesseg))
                teljes_szelesseg += ful_szelesseg
            
            teljes_szelesseg += max(0, len(ful_adatok) - 1) * ful_tavolsag
    
            x = self.szeleseg // 2 - teljes_szelesseg // 2
            y = 85
    
            for nev, adat, szoveg, ful_szelesseg in ful_adatok:
                adat["rect"] = pygame.Rect(x, y, ful_szelesseg, ful_magassag)
    
                if adat["klikd"]:
                    hatter = (46, 112, 158)
                    szegely = (115, 220, 255)
                    szoveg_szin = (255, 255, 255)
                else:
                    hatter = (24, 29, 37)
                    szegely = (75, 87, 102)
                    szoveg_szin = (175, 185, 195)
    
                pygame.draw.rect(self.screen, hatter, adat["rect"], border_radius=10)
    
                pygame.draw.rect(self.screen, szegely, adat["rect"], 2, border_radius=10)
    
                felirat = self.font_kis.render(nev, True, szoveg_szin)
    
                self.screen.blit(felirat,(adat["rect"].centerx - felirat.get_width() // 2, adat["rect"].centery - felirat.get_height() // 2,))
    
                x += ful_szelesseg + ful_tavolsag

            aktiv_oldal = None
    
            for nev, adat in self.settings_billentyu_modok.items():
                if adat["klikd"]:
                    aktiv_oldal = nev
                    break
            bill = {}
            for akcio, billentyu in self.billentyu_kiosztas.items():
                
                bill[akcio] = billentyu
            szeleseg = self.szeleseg // 7

            x1, x2, x3, x4 = szeleseg, szeleseg * 3, szeleseg*4, szeleseg* 6
            y = 200
            for nev, adat in self.settings_billentyu_modok.items():
                if adat.get("klikd"):
                    mood = nev

            for index, (nev, bb) in enumerate(bill[mood].items()):
                    szoveg = self.font_kis.render(nev, True, (250, 250, 250))
                    szoveg_rect = pygame.Rect(x1 if index%2==0 else x3, y-10, szoveg.get_width()+30, szoveg.get_height() + 10)
                    billentyu = self.font_kis.render(bb, True, (250, 250, 250))
                    b_rect = pygame.Rect(x2 if index%2==0 else x4, y-10, billentyu.get_width()+30, billentyu.get_height() + 10)
                    pygame.draw.rect(self.screen, (70, 70, 70), szoveg_rect, border_radius=15)
                    self.screen.blit(szoveg, (x1+15 if index%2==0 else x3+15, y-5))
                    pygame.draw.rect(self.screen, (100, 100, 100) if self.billentyu_rectek.get(nev).get("klikd") else (50,50,50) ,b_rect, border_radius=10)
                    self.screen.blit(billentyu, (x2+15 if index%2==0 else x4+15, y-5))
                    self.billentyu_rectek[nev]["rect"] = b_rect
                
                    if index%2==1: y+= 50

    def settings_event(self):
        def hangerot_beallit(kulcs, eger_x):
            slider_rect = self.settings_slider_rectek.get(kulcs)

            if slider_rect is None:
                return

            arany = (
                eger_x - slider_rect.x
            ) / slider_rect.width

            arany = max(0.0, min(1.0, arany))

            # 5%-os lépések.
            lepes = 0.05

            arany = round(arany / lepes) * lepes
            arany = max(0.0, min(1.0, arany))

            self.mousick_settings[kulcs] = arany

            # Azonnal alkalmazzuk a hangerőt.
            if kulcs == "backround_mousick":
                self.background_musick.set_volume(arany)

            elif kulcs == "tank_loves":
                self.hangok["sima_tank_loves"].set_volume(arany)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.settings_mentes()
                self.running = False

            elif event.type in (pygame.VIDEORESIZE, pygame.WINDOWRESIZED):
                uj_szelesseg, uj_magassag = pygame.display.get_window_size()
                self._atmeretezes(uj_szelesseg, uj_magassag)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.settings_huzott = None
                    self.settings_mentes()
                    self.statusz = "home"

                
                for nevv in self.billentyu_rectek.keys():
                    adat = self.billentyu_rectek.get(nevv)
                    if adat.get("klikd"):
                        for nev, adat in self.settings_billentyu_modok.items():
                            if adat.get("klikd"):
                                mood = nev 
                        name = pygame.key.name(event.key)

                        self.billentyu_json(read=False, mood=mood, valtosztando=nevv, ra=name)
                        self.billentyu_kiosztas = self.billentyu_json()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue

                oldalra_kattintott = False

                for nev, adat in self.settings_oldalak.items():
                    rect = adat.get("rect")

                    if rect and rect.collidepoint(event.pos):
                        oldalra_kattintott = True

                        for masik_adat in self.settings_oldalak.values():
                            masik_adat["klikd"] = False

                        adat["klikd"] = True
                        self.settings_huzott = None
                        break

                if self.settings_oldalak.get("Billentyű").get("klikd"):
                    for nev, adat in self.settings_billentyu_modok.items():
                        rect = adat.get("rect")
                        if rect and rect.collidepoint(event.pos):
                            oldalra_kattintott = True
                            for j in self.settings_billentyu_modok.values():
                                j["klikd"] = False

                            adat["klikd"] = True
                            break


                    for nev, adat in self.billentyu_rectek.items():
                        rect = adat.get("rect")
                        if rect and rect.collidepoint(event.pos):
                            for j in self.billentyu_rectek.values():
                                j["klikd"] = False
                            adat["klikd"]=True
                            break


                if oldalra_kattintott:
                    continue

                if self.settings_vissza and self.settings_vissza.collidepoint(event.pos):
                    self.statusz = self.elozo_statusz

                

                hang_oldal_aktiv = self.settings_oldalak.get("Hangok", {}).get("klikd", False)

                if hang_oldal_aktiv:
                    for kulcs, slider_rect in self.settings_slider_rectek.items():
                        nagyobb_kattintasi_terulet = slider_rect.inflate(
                            28,
                            36
                        )

                        if nagyobb_kattintasi_terulet.collidepoint(event.pos):
                            self.settings_huzott = kulcs

                            hangerot_beallit(
                                kulcs,
                                event.pos[0]
                            )

                            break

            elif event.type == pygame.MOUSEMOTION:
                if self.settings_huzott is not None:
                    hangerot_beallit(
                        self.settings_huzott,
                        event.pos[0]
                    )

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.settings_huzott is not None:
                    hangerot_beallit(
                        self.settings_huzott,
                        event.pos[0]
                    )

                    self.settings_huzott = None

                    # Nem minden egérmozdulatnál írjuk a fájlt,
                    # csak amikor a játékos elengedi a csúszkát.
                    self.settings_mentes()

    def billentyu_json(self, read=True, mood="platformer", valtosztando="up", ra="space"):
        if read:
            if os.path.exists(self.path_settings_billentyu):
                with open(self.path_settings_billentyu, "r", encoding="utf-8") as f:
                    tartalom = f.read().strip()
                    return json.loads(tartalom)
        else:
            with open(self.path_settings_billentyu, "w", encoding="utf-8") as f:
                menteni_kivant = {
                    i: {"up": ra if mood==i and valtosztando=="up" else self.billentyu_kiosztas.get(i, "platformer").get("up", "space"),
                        "down": ra if mood==i and valtosztando=="down" else self.billentyu_kiosztas.get(i, "platformer").get("down", "s"),
                        "left": ra if mood==i and valtosztando=="left" else self.billentyu_kiosztas.get(i, "platformer").get("left", "a"),
                        "right": ra if mood==i and valtosztando=="right" else self.billentyu_kiosztas.get(i, "platformer").get("right", "d"),
                        "bumm": ra if mood==i and valtosztando=="bumm" else self.billentyu_kiosztas.get(i, "platformer").get("bumm", "j"),
                        "pause": ra if mood==i and valtosztando=="pause" else self.billentyu_kiosztas.get(i, "platformer").get("pause", "kescape")
                        } for i in self.settings_billentyu_modok.keys()
                    }
                json.dump(menteni_kivant, f, indent=2, ensure_ascii=False)

    
    def _tankos_terkep_rajzolas(self, rajzolt_allapot):
        terkep = rajzolt_allapot.get("terkep_resz")

        if not terkep:
            return

        adatok = terkep.get("adatok", [])
        cella = int(terkep.get("cella", 40))
        start_sor = int(terkep.get("start_sor", 0))
        start_oszlop = int(terkep.get("start_oszlop", 0))




        vilag_sorok = math.ceil(rajzolt_allapot["vilag_magassag"] / cella)
        vilag_oszlopok = math.ceil(rajzolt_allapot["vilag_szelesseg"] / cella)

        lathato_start_sor = int(self.kamera_y // cella) - 2
        lathato_veg_sor = int((self.kamera_y + self.magassag) // cella) + 3

        lathato_start_oszlop = int(self.kamera_x // cella) - 2
        lathato_veg_oszlop = int((self.kamera_x + self.szeleseg) // cella) + 3

        for sor in range(lathato_start_sor, lathato_veg_sor):
            for oszlop in range(lathato_start_oszlop, lathato_veg_oszlop):

                palyan_kivul = (sor < 0 or oszlop < 0 or sor >= vilag_sorok or oszlop >= vilag_oszlopok)
                if not palyan_kivul:
                    continue

                x = oszlop * cella - self.kamera_x
                y = sor * cella - self.kamera_y

                szin = self.fal_kepek["kozep"]

                self.screen.blit(szin, (int(x), int(y)))


        def fal_e(sor, oszlop):
            helyi_sor = sor - start_sor
            helyi_oszlop = oszlop - start_oszlop

            if helyi_sor < 0 or helyi_oszlop < 0:
                return False
            if helyi_sor >= len(adatok):
                return False
            if helyi_oszlop >= len(adatok[helyi_sor]):
                return False

            return adatok[helyi_sor][helyi_oszlop] == 1

        for helyi_sor, sor_adat in enumerate(adatok):
            vilag_sor = start_sor + helyi_sor
            
            

            for helyi_oszlop, ertek in enumerate(sor_adat):
                vilag_oszlop = start_oszlop + helyi_oszlop
                
                x = vilag_oszlop * cella - self.kamera_x
                y = vilag_sor * cella - self.kamera_y

                if ertek == 1:  # fal
                    van_fal_fent = fal_e(vilag_sor - 1, vilag_oszlop)
                    van_fal_lent = fal_e(vilag_sor + 1, vilag_oszlop)
                    van_fal_bal = fal_e(vilag_sor, vilag_oszlop - 1)
                    van_fal_jobb = fal_e(vilag_sor, vilag_oszlop + 1)

                    szomszed_falak = (int(van_fal_fent) + int(van_fal_lent) + int(van_fal_bal) + int(van_fal_jobb))

                    
                    if szomszed_falak == 0:
                        fold = self.fal_kepek["kovek"]
                        index = (vilag_sor * 31 + vilag_oszlop * 17) % len(fold) -1
                        alap = self.talaj_kepek["koves"][index]
                        self.screen.blit(alap, (int(vilag_oszlop * cella - self.kamera_x), int(vilag_sor * cella - self.kamera_y)))
                        kovek = self.fal_kepek["kovek"]
                        index = (vilag_sor * 31 + vilag_oszlop * 17) % len(kovek)
                        szin = kovek[index]

                    
                    elif szomszed_falak == 1:
                        if van_fal_fent:
                            szin = self.fal_kepek["3_alul"]
                        elif van_fal_lent:
                            szin = self.fal_kepek["3_fent"]
                        elif van_fal_bal:
                            szin = self.fal_kepek["3_jobbra"]
                        elif van_fal_jobb:
                            szin = self.fal_kepek["3_balra"]
                    
                    elif szomszed_falak == 2:
                        if not van_fal_fent and not van_fal_bal:
                            szin = self.fal_kepek["bal_fent"]

                        elif not van_fal_fent and not van_fal_jobb:
                            szin = self.fal_kepek["jobb_fent"]

                        elif not van_fal_lent and not van_fal_bal:
                            szin = self.fal_kepek["bal_lent"]

                        elif not van_fal_lent and not van_fal_jobb:
                            szin = self.fal_kepek["jobb_lent"]

                        elif van_fal_fent and van_fal_lent:
                            szin = self.fal_kepek["bal_jobb"]

                        elif van_fal_jobb and van_fal_bal:
                            szin = self.fal_kepek["fent_lent"]

                    
                    else:
                        if not van_fal_fent:
                            szin = self.fal_kepek["fent"]

                        elif not van_fal_lent:
                            szin = self.fal_kepek["lent"]

                        elif not van_fal_bal:
                            szin = self.fal_kepek["bal"]

                        elif not van_fal_jobb:
                            szin = self.fal_kepek["jobb"]

                        else:
                            szin = self.fal_kepek["kozep"]

                elif ertek == 0:
                    fold = self.fal_kepek["kovek"]
                    index = (vilag_sor * 31 + vilag_oszlop * 17) % len(fold) -1
                    szin = self.talaj_kepek["koves"][index]

                elif ertek == 2:
                    szin = (50, 50, 255)

                elif ertek == -1:
                    szin = (255, 0, 0)

                elif ertek == 3:
                    fold = self.fal_kepek["kovek"]
                    index = (vilag_sor * 31 + vilag_oszlop * 17) % len(fold) -1
                    szin = self.talaj_kepek["koves"][index]
                    
                    self.screen.blit(szin, (int(x), int(y)))
                    szin = self.talaj_kepek["chest"]

                

                if isinstance(szin, pygame.Surface):
                    self.screen.blit(szin, (int(x), int(y)))
                else:
                    pygame.draw.rect(
                        self.screen,
                        szin,
                        (int(x), int(y), cella, cella)
                    )

    def _kigyo_rajzolas(self, kigyo: dict):
        pontok = kigyo.get("test_pontok", [])
        for index in range(len(pontok) - 1, -1, -1):
            x, y = pontok[index]
            szin = tuple(kigyo["fej_szin"]) if index == 0 else tuple(kigyo["szin"])
            pygame.draw.circle(self.screen, szin, (int(x - self.kamera_x), int(y - self.kamera_y)), int(kigyo.get("sugar", self.beallitasok.kigyó_sugár)))
        if pontok:
            fej_x, fej_y = pontok[0]
            nev = self.font_kis.render(kigyo["nev"], True, (255, 255, 255))
            self.screen.blit(nev, (int(fej_x - self.kamera_x - nev.get_width() // 2), int(fej_y - self.kamera_y - 36)))

    def _jatek_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self._atmeretezes(event.w, event.h)
            if self.halozati_mod == "single":
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_p):
                        self.paused = not self.paused if self.halozati_mod == "single" else self.paused
            if not self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN and self.pause_gomb.collidepoint(event.pos):
                    if self.halozati_mod == "single":
                        self.paused = not self.paused
            if self.paused and self.halozati_mod == "single":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for kulcs, adat in self.pause_gombok.items():
                        if adat["rect"] and adat["rect"].collidepoint(event.pos):
                            if kulcs == "resume":
                                self.paused = False
                            elif kulcs == "new game":
                                self._single_inditas()

                            elif kulcs == "main menu":
                                if not self.mentes_megtortent_e:
                                    self.mentes_megtortent_e = True
                                    most = datetime.now()
                                    adat = {
                                
                                        "nev": self.nev,
                                        "szin": self.szin,
                                        "mode": self.jatek_mode,
                                        "nehezseg": self.nehezseg_szint,
                                        "hoszusag": self.testhossz,
                                        "olesek": self.olesek,
                                        "alma_pontszam": self.pontszam,
                                        "ido": self.ido,
                                        "befejezesi_ido": {
                                            "ev": most.year,
                                            "honap": most.month, 
                                            "nap": most.day, 
                                            "ora": most.hour, 
                                            "perc": most.minute, 
                                            "masodperc": most.second, 
                                            "micromasodperc":most.microsecond,
                                            },


                                    }
                                    mentes(adat)
                                self._fo_menu_vissza()
                            elif kulcs == "settings":
                                self.statusz = "settings"
                                self.elozo_statusz = "jatek"
                                return
            if self.is_mobile and event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                fid = event.finger_id
                if event.type == pygame.FINGERUP:
                    if fid in self.ujjak:
                        del self.ujjak[fid]
                else:
                    self.ujjak[fid] = (event.x * self.szeleseg, event.y * self.magassag)
                    
                self.joystick_irany_x = 0.0
                self.joystick_irany_y = 0.0
                self.mobil_loves = False
                
                for ujj_id, (tx, ty) in self.ujjak.items():
                    j_dx = tx - self.joystick_kozep[0]
                    j_dy = ty - self.joystick_kozep[1]
                    j_tav = math.hypot(j_dx, j_dy)
                    
                    if j_tav <= self.joystick_sugar * 1.8:
                        if j_tav > 0:
                            korlat = min(j_tav, self.joystick_sugar)
                            self.joystick_irany_x = (j_dx / j_tav) * (korlat / self.joystick_sugar)
                            self.joystick_irany_y = (j_dy / j_tav) * (korlat / self.joystick_sugar)
                            
                    
                    g_tav = math.hypot(tx - self.gomb_kozep[0], ty - self.gomb_kozep[1])
                    if g_tav <= self.gomb_sugar:
                        self.mobil_loves = True
            
    def _pause_rajzolas(self):
        felulet = pygame.Surface((self.szeleseg, self.magassag), pygame.SRCALPHA)
        felulet.fill((0, 0, 0, 160))
        self.screen.blit(felulet, (0, 0))
        pause_txt = self.font_nagy.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_txt, (self.szeleseg // 2 - pause_txt.get_width() // 2, self.magassag // 2 - 120))
        for index, kulcs in enumerate(self.pause_gombok):
            szin = (100, 255, 100) if kulcs == "resume" else (255, 255, 0) if kulcs == "main menu" else (255, 0, 0)
            rect = pygame.Rect(self.szeleseg // 2 - 330 + index * 220, self.magassag // 2 + 20, 200, 54)
            self.pause_gombok[kulcs]["rect"] = rect
            pygame.draw.rect(self.screen, szin, rect)
            felirat = self.font_kis.render(kulcs, True, (0, 0, 0) if kulcs != "quit" else (255, 255, 255))
            self.screen.blit(felirat, (rect.x + 44, rect.y + 16))
        
    def _hud_panel(self, rect, hatter=(12, 16, 22, 220), szegely=(110, 135, 155, 230)):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)

        pygame.draw.rect(panel, hatter, panel.get_rect(), border_radius=14)

        pygame.draw.rect(panel, szegely, panel.get_rect(), 2, border_radius=14)

        self.screen.blit(panel, rect.topleft)


    def _buff_ertek_szoveg(self, nev, ertek):
        if nev == "teleport":
            return "?"

        try:
            ertek = float(ertek)
        except (TypeError, ValueError):
            return "?"

        if nev.startswith("shild"):
            szazalek = abs(1.0 - ertek) * 100
            jel = "+" if nev.endswith("+") else "-"
            return f"{jel}{szazalek:.0f}%"

        if nev.startswith("bulet"):
            alap = self.beallitasok.loves_cooldown
            szazalek = (alap - ertek) / alap * 100
            return f"{szazalek:+.0f}%"

        if nev.startswith("rotate"):
            elteres = ertek - 100
            return f"{elteres:+.0f}"

        if ertek.is_integer():
            return f"{ertek:+.0f}"

        return f"{ertek:+.1f}"

    def _aktiv_buff_sav_rajzolas(self, buffok):
        if self.buffok is None:
            return

        buffok = [buff for buff in buffok if buff.get("cel_ido", 0) > 0]

        if not buffok:
            return

        ikon_meret = 52
        tav = 16
        felso_resz = 24
        also_resz = 22

        sav_szelesseg = len(buffok) * ikon_meret + (len(buffok) + 1) * tav
        sav_magassag = felso_resz + ikon_meret + also_resz

        x0 = (self.szeleseg - sav_szelesseg) // 2
        y0 = self.magassag - sav_magassag - 18

        sav_rect = pygame.Rect(x0, y0, sav_szelesseg, sav_magassag)

        self._hud_panel(sav_rect, hatter=(8, 10, 14, 225), szegely=(90, 105, 120, 230))

        for index, buff in enumerate(buffok):
            nev = buff["nev"]
            ertek = buff["ertek"]

            x = x0 + tav + index * (ikon_meret + tav)
            y = y0 + felso_resz

            ikon_rect = pygame.Rect(x, y, ikon_meret, ikon_meret)

            pozitiv = nev.endswith("+")
            negativ = nev.endswith("-")

            if pozitiv:
                szin = (90, 235, 125)
            elif negativ:
                szin = (245, 85, 85)
            else:
                szin = (180, 110, 255)

            pygame.draw.rect(self.screen, (20, 24, 30), ikon_rect.inflate(8, 8), border_radius=10)

            pygame.draw.rect(self.screen, szin, ikon_rect.inflate(8, 8), 2, border_radius=10)

            cel_ido = max(0.001, float(buff["cel_ido"]))
            eltelt_ido = float(buff["eltelt_ido"])

            hatralevo_ido = max(0.0, cel_ido - eltelt_ido)
            arany = max(0.0, min(1.0, hatralevo_ido / cel_ido))

            kor_rect = ikon_rect.inflate(12, 12)

            pygame.draw.arc( self.screen, (55, 60, 70), kor_rect, 0, math.tau, 4)

            pygame.draw.arc(self.screen, szin, kor_rect, -math.pi / 2, -math.pi / 2 + math.tau * arany, 4)

            self.buffok.hud_buff_rajzolas(self.screen, nev, ikon_rect.centerx, ikon_rect.centery, ikon_meret - 8)

            ertek_szoveg = self.font_mini.render(self._buff_ertek_szoveg(nev, ertek), True, szin)

            self.screen.blit(ertek_szoveg, (ikon_rect.centerx - ertek_szoveg.get_width() // 2, y0 + 3,))

            ido_szoveg = self.font_mini.render(f"{hatralevo_ido:.1f}", True, (235, 235, 235))

            self.screen.blit(ido_szoveg, (ikon_rect.centerx - ido_szoveg.get_width() // 2, ikon_rect.bottom + 8,))

    def _tankos_felso_hud_rajzolas(self, sajat, tank_db):
        panel_rect = pygame.Rect(16, 16, 280, 112)

        self._hud_panel(panel_rect, hatter=(10, 15, 20, 225), szegely=(95, 130, 165, 235))

        tank_szin = tuple(sajat.get("szin", (90, 160, 255)))

        pygame.draw.circle(self.screen, tank_szin, (48, 49), 18)

        pygame.draw.circle(self.screen, (230, 235, 245), (48, 49), 18, 2)

        nev = sajat.get("nev", "Játékos")

        nev_szoveg = self.font_kozep.render(nev, True, (245, 245, 245))

        self.screen.blit(nev_szoveg, (76, 26))

        hp = float(sajat.get("hp", 0))
        max_hp = max(1.0, float(sajat.get("max_hp", 100)))

        hp_szoveg = self.font_kis.render(f"HP: {hp:.0f} / {max_hp:.0f}", True, (115, 245, 140))

        self.screen.blit(hp_szoveg, (76, 55))

        hp_arany = max(0.0, min(1.0, hp / max_hp))

        hp_hatter = pygame.Rect(76, 80, 178, 14)
        hp_toltes = pygame.Rect( hp_hatter.x, hp_hatter.y, int(hp_hatter.width * hp_arany), hp_hatter.height)

        pygame.draw.rect(self.screen, (45, 50, 58), hp_hatter, border_radius=7)

        hp_szin = (100, 235, 125) if hp_arany > 0.3 else (245, 85, 85)

        pygame.draw.rect( self.screen, hp_szin, hp_toltes, border_radius=7)

        also_szoveg = self.font_mini.render(f"Találatok: {sajat.get('pontok', 0)}     Ölések: {sajat.get('olesek', 0)}", True, (220, 220, 225))

        self.screen.blit(also_szoveg, (24, 99))

        felso_szoveg = (
            f"Idő: {self.ido:.0f}    "
            f"Tankok: {tank_db}    "
            f"Koordináta: {self.koordinata_szoveg}"
        )

        felirat = self.font_kis.render(felso_szoveg, True, (245, 245, 245))

        felso_rect = pygame.Rect(self.szeleseg // 2 - felirat.get_width() // 2 - 18, 16, felirat.get_width() + 36, 40)

        self._hud_panel(felso_rect, hatter=(8, 12, 17, 225), szegely=(85, 95, 110, 220))

        self.screen.blit(felirat,(felso_rect.centerx - felirat.get_width() // 2, felso_rect.centery - felirat.get_height() // 2,))

        if not self.halozat:
            self.pause_gomb = pygame.Rect(self.szeleseg - 124, 16, 108, 40)

            self._hud_panel(self.pause_gomb, hatter=(38, 78, 62, 230), szegely=(105, 245, 145, 235))

            pause_txt = self.font_kis.render("PAUSE", True, (235, 255, 240))

            self.screen.blit(pause_txt, (self.pause_gomb.centerx - pause_txt.get_width() // 2, self.pause_gomb.centery - pause_txt.get_height() // 2,))

    def _halott_rajzolas(self):
        #felulet = pygame.Surface((self.szeleseg, self.magassag), pygame.SRCALPHA)
        #felulet.fill((0, 0, 0, 160))
        #self.screen.blit(felulet, (0, 0))
        halott_txt = self.font_nagy.render("MEGHALTÁL", True, (255, 50, 50))
        self.screen.blit(halott_txt, (self.szeleseg // 2 - halott_txt.get_width() // 2, self.magassag // 2 - 100))
        self.ujraindulas_gomb = pygame.Rect(self.szeleseg // 2 - 120, self.magassag // 2 + 40, 240, 54)
        self.kilepes_gomb = pygame.Rect(self.szeleseg // 2 - 120, self.magassag // 2 + 110, 240, 54)
        pygame.draw.rect(self.screen, (0, 255, 0), self.ujraindulas_gomb)
        pygame.draw.rect(self.screen, (255, 50, 50), self.kilepes_gomb)
        uj_txt = self.font_kozep.render("Újrajátszás", True, (0, 0, 0))
        ki_txt = self.font_kozep.render("Kilépés", True, (255, 255, 255))
        self.screen.blit(uj_txt, (self.ujraindulas_gomb.x + 25, self.ujraindulas_gomb.y + 12))
        self.screen.blit(ki_txt, (self.kilepes_gomb.x + 62, self.kilepes_gomb.y + 12))
        #pygame.display.update()

    def _halott_event(self):
        if not self.mentes_megtortent_e:
            self.mentes_megtortent_e = True
            most = datetime.now()
            adat = {
          
                "nev": self.nev,
                "szin": self.szin,
                "mode": self.jatek_mode,
                "nehezseg": self.nehezseg_szint,
                "hoszusag": self.testhossz,
                "olesek": self.olesek,
                "alma_pontszam": self.pontszam,
                "ido": self.ido,
                "befejezesi_ido": {
                    "ev": most.year,
                    "honap": most.month, 
                    "nap": most.day, 
                    "ora": most.hour, 
                    "perc": most.minute, 
                    "masodperc": most.second, 
                    "micromasodperc":most.microsecond,
                    },
            }
            mentes(adat)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self._atmeretezes(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.ujraindulas_gomb and self.ujraindulas_gomb.collidepoint(event.pos):
                    if self.halozati_mod == "single":
                        if self.jatek_mode == "tankos":
                            self.helyi_vilag.folytatas((self.helyi_jatekos_id, self.nev, self.szin, self.tank.tank))
                        else:
                            self.helyi_vilag.folytatas((self.helyi_jatekos_id, self.nev, self.szin, None))

                            
                        self.mentes_megtortent_e = False
                        self.utolso_allapot = self.helyi_vilag.nezet_jatekosnak(self.helyi_jatekos_id, self.szeleseg, self.magassag)
                    else:
                        self.halozat.kuldd({"tipus": "ujraindulas"})
                    self.statusz = "jatek"
                    self.halal_allapot = None
                    self.mentes_megtortent_e = False
                elif self.kilepes_gomb and self.kilepes_gomb.collidepoint(event.pos):
                    if self.halozat:
                        self.halozat.kuldd({"tipus": "szobabol_kilepes"})
                    self._fo_menu_vissza()
    
    def rang_lista_rajzolas(self):
        szoveg = []
        felso_szoveg = self.font_mini.render("név     testhossz   olesek      pontszám", True, (255, 50, 50))
        szoveg.append(felso_szoveg)
        # self.screen.blit(felso_szoveg, (self.szeleseg - felso_szoveg.get_width() + 10, 3))
        rajzolt_allapot = self.halal_allapot if self.statusz == "halott" and self.halal_allapot else self.utolso_allapot
        try:
            for nev, testhossz, oles, pontszam in rajzolt_allapot["toplista"]:
                szoveg.append(self.font_mini.render(f"{nev}   {testhossz}     {oles}    {pontszam}", True, (255, 50, 50)))
        except:
            pass
        elozo = felso_szoveg
        for index, szov in enumerate(szoveg):
            self.screen.blit(szov, (self.szeleseg - felso_szoveg.get_width() - 10, (index + 1) * 5 + elozo.get_height() * index))
            elozo = szov
      
    def backround_musick_playing(self):
        if self.background_musick.get_busy():
            return
        self.background_musick.set_volume(self.mousick_settings["backround_mousick"])
        self.background_musick.play(self.hangok["bacground"][random.randint(1, 6)])


        
    """def platformer_terkep_betolto(self, szoba):
        if szoba == "":
            szoba = "1_kezdo_szoba.json"
        hely = os.path.join(self.platformer_file_helye, str(szoba))
        with open(hely, "r", encoding="utf8") as f:
            world = json.loads(f.read().strip())
        self.platformer_terkep = world"""

    def platformer_terkep_betolto(self, szoba):
        fajl = os.path.join(os.path.dirname(__file__), "p1.ldtk")
        self.platformer_terkep = ldtk_terkep_betoltes(fajl, szoba if szoba else None)
        self.jelenlegi_szoba = self.platformer_terkep["szoba"]

        self.platformer_tileset = pygame.image.load(os.path.join(os.path.dirname(__file__), "SunnyLand_by_Ansimuz-extended.png")).convert_alpha()
        self.platformer_tile_cache = {}

        zoom = self.platformer_zoom

        for reteg in self.platformer_terkep["rajz_retegek"]:
            meret = reteg["tile_meret"]
            reteg["rajz_racs"] = {}

            for tile in reteg["tileok"]:
                alpha = max(0, min(255, int(tile["alpha"] * reteg["opacity"] * 255)))
                kulcs = (tile["src_x"], tile["src_y"], meret, tile["flip"], alpha, zoom)
                kep = self.platformer_tile_cache.get(kulcs)

                if kep is None:
                    kep = self.platformer_tileset.subsurface(pygame.Rect(tile["src_x"], tile["src_y"], meret, meret)).copy()

                    if tile["flip"]:
                        kep = pygame.transform.flip(kep, bool(tile["flip"] & 1), bool(tile["flip"] & 2))

                    if alpha < 255:
                        kep.set_alpha(alpha)

                    if zoom != 1:
                        kep = pygame.transform.scale(kep, (int(meret * zoom), int(meret * zoom)))

                    self.platformer_tile_cache[kulcs] = kep

                tile["kep"] = kep

                cella_x = int(tile["x"] // meret)
                cella_y = int(tile["y"] // meret)
                reteg["rajz_racs"].setdefault((cella_x, cella_y), []).append(tile)

    def run(self):
        while self.running:
            self.backround_musick_playing()
            delta_ido = self.clock.tick(self.beallitasok.fps) / 1000.0
            if self.statusz == "home":
                self._home_rajzolas()
                self._home_event()
            elif self.statusz == "ranglistak":
                self.ranglistak_rajzolas()
                self.ranglistak_event()
            elif self.statusz == "varakozas":
                self._varakozas_rajzolas()
                self._varakozas_event()
            elif self.statusz == "jatek":
                if self.jatek_mode == "platformer":
                    if self.elozo_jelenlegi_szoba != self.jelenlegi_szoba:
                        self.platformer_terkep_betolto(self.jelenlegi_szoba)
                        self.elozo_jelenlegi_szoba = self.jelenlegi_szoba
                self._frissits_allapotot(delta_ido)
                self._jatek_rajzolas(delta_ido)
                self._jatek_event()
                if self.jatek_mode == "alma":
                    self.rang_lista_rajzolas()
                
            elif self.statusz == "settings":
                self.settings_rajzolas()
                self.settings_event()
            elif self.statusz == "halott":
                if self.halozati_mod == "single" and self.helyi_vilag:
                    self.helyi_vilag.frissites(delta_ido)
                elif self.halozat:
                    uj = self.halozat.legfrissebb_allapot()
                    if uj is not None:
                        self.utolso_allapot = uj

                self._jatek_rajzolas(delta_ido)
                self._halott_rajzolas()
                self._halott_event()
            if self.halozat and self.halozat.init_megkapva and not self.platformer_halozat_meretezes:
                self.halozat.kuldd({"tipus": "kep_beallitas", "azonosito":self.halozat.sajat_id, "width":"width", "height": "height", "kep": "", "x": self.jatekos.kepek["Idle"][0].get_width() / self.platformer_zoom, "y": self.jatekos.kepek["Idle"][0].get_height() / self.platformer_zoom})
                self.platformer_halozat_meretezes = True             
            pygame.display.update()
        if self.halozat:
            self.halozat.leallit()
        pygame.quit()



jatek = Alap()
jatek.run()
