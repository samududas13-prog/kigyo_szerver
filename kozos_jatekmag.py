import math
import random
import numpy as np
import os
import json
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
from nevek_10000 import NEVEK
from p_terkem_beolvasasa import ldtk_terkep_betoltes

class Beallitasok:
    def __init__(self):
        self.vilag_szelesseg = 15000
        self.vilag_magassag = 15000  
        self.tank_vilag_szelesseg = 50
        self.tank_vilag_magassag = 50
        self.racsok_nagysaga = 200
        self.fps = 50
        self.szerver_fps = 30 
        self.kezdes = True
        self.platformer_zoom = 3
        self.platformer_jatekos_mozgas_szorzo = 60
        self.platformer_ugras = -7
        self.gyorsulas_csokentes = 0.55
        self.gravitacio = 0.3
        self.alap_gravitacio = self.gravitacio
        self.max_gravitacio = 5

        self.kigyó_sugár = 20 
        self.kigyo_alap_hossz = 4  
        self.kigyo_resz_tav = 28 
        self.kigyo_novekedes_alma_db = 1  
        self.kigyo_no = 3 
        self.kigyo_csokenes_sebeseg = 10 
        self.kigyo_rajzolas_puffer = 100  
        self.kigyo_lathato_pont_limit = 500
        self.kigyo_utkozes_szorzo = 1.75 
        self.kigyo_onvedo_index = 1 
        self.kigyo_dontesi_szogek = [-60, -45, -30, -15, 0, 15, 30, 45, 60] 
        self.kigyo_veszely_puffer = 3.0 
        self.kigyo_lato_ido = 60 
        self.kigyo_max_memoria_szorzo = 6 
        self.kigyo_respawn_varakozas = 24 
        self.kigyo_spawn_puffer = 220 

        self.alma_size = 25 
        self.alma_kor_sugár = 12.5  
        self.alma_maximum = 10000  
        self.alma_potlasi_limit = 50  
        self.alma_lathato_limit = 700  
        self.alma_rajzolas_puffer = 60 

        self.jatekos_sugar = 25  
        self.jatekos_sebesseg = 500.0
        self.jatekos_hp = 100  
        self.jatekos_utkozes_puffer = 2.0 

        self.loves_cooldown = 0.5

        self.pause_gomb_szelesseg = 200 
        self.pause_gomb_magassag = 50 
        
        self.szoba_kod_hossz = 5
        self.szerver_alap_port = 20000 
        self.szerver_port_tartomany = 30000 
        self.felfedezo_port = 37021  
        self.felfedezo_valasz_ido = 2.5

        self.buffok_szelesege = 60
        self.buff_kijelzes_felszedeskor_ido = 2
        
        self.dontes_gyakorisag = 5
        self.kigyo_max_fordulas_fok = 100
        self.top_hany = 5
        self.szerver_kliens_szabályuzott_kuldes = 5

        self.tank_kepek = ["tank_1_kek", "tank_2_kek", "tank_3_kek", "tank_4_kek"]
        
        self.chest_kincsek = [["hp", "hp+", "hp-"], ["speed", "speed+", "speed-"],  ["kill", "kill+", "kill-"],  ["shild", "shild+",  "shild-"], ["rotate", "rotate+", "rotate-"], ["bulet", "bulet+", "bulet-"], ["teleport", "teleport", "teleport"]]

        self.buff_ertekek = {
            "teleport": {
                "ertek": [None],
                "ido": [0],
            },

            "hp+": {
                "ertek": [40, 15, 20, 25, 30, 35, 40],
                "ido": [0],
            },
            "hp-": {
                "ertek": [-8, -12, -16, -20, -25, -30, -35],
                "ido": [0],
            },

            "kill+": {
                "ertek": [1, 1, 1, 1, 1, 2, 2, 2, 3],
                "ido": [0],
            },
            "kill-": {
                "ertek": [-1, -1, -1, -2, -2, -2, -3],
                "ido": [0],
            },

            # Lövési cooldown: kisebb = gyorsabb lövés.
            "bulet+": {
                "ertek": [0.42, 0.38, 0.34, 0.30, 0.26, 0.22, 0.18],
                "ido":   [5,    6,    7,    8,    9,   10,   12],
            },
            "bulet-": {
                "ertek": [0.70, 0.80, 0.95, 1.10, 1.30, 1.50, 1.80],
                "ido":   [5,    6,    7,    8,    9,   10,   12],
            },

            # Fordulási sebesség fok / másodpercben.
            "rotate+": {
                "ertek": [120, 140, 160, 180, 210, 240, 280],
                "ido":   [5,   6,   7,   8,   9,   10,  12],
            },
            "rotate-": {
                "ertek": [85, 75, 65, 55, 45, 35, 25],
                "ido":   [5,  6,  7,  8,  9,  10, 12],
            },

            # Pajzs: kisebb érték = kevesebb kapott sebzés.
            "shild+": {
                "ertek": [0.85, 0.78, 0.70, 0.62, 0.55, 0.48, 0.40],
                "ido":   [5,    6,    7,    8,    9,   10,   12],
            },
            "shild-": {
                "ertek": [1.15, 1.25, 1.35, 1.50, 1.65, 1.80, 2.00],
                "ido":   [5,    6,    7,    8,    9,   10,   12],
            },

            # Sebesség: a jelenlegi += rendszerhez.
            "speed+": {
                "ertek": [40, 60, 80, 100, 130, 160, 200],
                "ido":   [5,  6,  7,  8,   9,  10,  12],
            },
            "speed-": {
                "ertek": [-35, -50, -70, -90, -120, -150, -190],
                "ido":   [5,    6,   7,   8,    9,   10,   12],
            },
        }
                

        self.nehezseg_atvalto = {
            "Easy": 3,
            "Normal": 5,
            "Hard": 7,
            "Nightmare": 10,
            "Hell": 20,
        }


        self.utes_cooldown = 1

class KorSeged:
    @staticmethod
    def tavolsag(x1: float, y1: float, x2: float, y2: float) :
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def normalizal(dx: float, dy: float):
        hossz = math.hypot(dx, dy)
        if hossz < 1e-6:
            return 0.0, 0.0
        return dx / hossz, dy / hossz

    @staticmethod
    def korok_utkozne_e(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float):
        return math.hypot(x2 - x1, y2 - y1) < (r1 + r2)

    @staticmethod
    def kulcs(racsok_nagysaga: int, x: float, y: float):
        return int(x // racsok_nagysaga), int(y // racsok_nagysaga)

    @staticmethod
    def szomszed_kulcsok(racsok_nagysaga: int, x: float, y: float, sugar: float, extra: int = 1):
        cx, cy = KorSeged.kulcs(racsok_nagysaga, x, y)
        raszter = max(1, int(math.ceil(sugar / racsok_nagysaga))) + extra
        for rx in range(cx - raszter, cx + raszter + 1):
            for ry in range(cy - raszter, cy + raszter + 1):
                yield rx, ry

    @staticmethod
    def dobozok_utkozne_e(x1: float, y1: float, sz1: float, m1: float, x2: float, y2: float, sz2: float, m2: float):
        """x,y: bal-felso sarok; sz: szelesseg; m: magassag"""
        return x1 < x2 + sz2 and x1 + sz1 > x2 and y1 < y2 + m2 and y1 + m1 > y2


class SzinSeged:
    @staticmethod
    def veletlen_szin():
        return random.randint(20, 255), random.randint(20, 255), random.randint(20, 255)

    @staticmethod
    def fej_szin(szin):
        return min(255, szin[0] + 40), min(255, szin[1] + 40), min(255, szin[2] + 40)

class Chest:
    def __init__(self, azonosito: str, x: float, y: float, beallitasok: Beallitasok, cellax, cellay, vilag):
        self.azonosito = azonosito
        self.x = x
        self.y = y
        self.cella_x = cellax
        self.cella_y = cellay
        self.hp = 1
        self.kincs = random.choice(beallitasok.chest_kincsek)
        self.alap_kep = self.kincs[0]
        valasztas = random.randint(1, 2)
        self.buff = self.kincs[valasztas]
        ertek = beallitasok.buff_ertekek.get(self.buff).get("ertek")
        self.ertek = random.choice(ertek) if self.buff != "teleport" else vilag
        ido = beallitasok.buff_ertekek.get(self.buff).get("ido")
        self.ido = random.choice(ido)
        self.el = True
        self.kincs_lathato = False
        self.pajzs = 1
        self.sugar = beallitasok.buffok_szelesege // 2 + 5

    def allapot_dict(self):
        return {
            "azonosito": self.azonosito,
            "x": self.x,
            "y": self.y,
            "kincs_fajta": self.alap_kep,
            "kincs": self.buff,
        }

class Tanki:
    def __init__(self, azonosito: str, nev: str, szin: Tuple[int, int, int], x: float, y: float, beallitasok: Beallitasok):
        self.azonosito = azonosito
        self.nev = nev 
        self.szin = szin 
        self.x = x 
        self.y = y 
        self.sugar = beallitasok.jatekos_sugar
        self.sebesseg = beallitasok.jatekos_sebesseg
        self.alap_sebesseg = self.sebesseg
        self.alap_hp = float(beallitasok.jatekos_hp)
        self.hp = self.alap_hp
        self.el = True 
        self.mozog_balra = False 
        self.mozog_jobbra = False 
        self.mozog_fel = False
        self.mozog_le = False 
        self.loves = False
        self.tuzelt = False
        self.loves_cooldown = beallitasok.loves_cooldown
        self.loves_idozito = beallitasok.loves_cooldown -0.3
        self.loves_cooldown_alap = self.loves_cooldown
        self.eltelt_ido = 0.0
        self.fok = random.randint(1, 360)
        self.fordulasi_sebesseg = 100
        self.fordulasi_sebesseg_alap = self.fordulasi_sebesseg
        self.utolso_racs = None
        self.tank_kep_nev = random.choice(beallitasok.tank_kepek)
        self.jatekos_e = False
        self.gondolkozasi_ido = 5
        self.olesek = 0
        self.olesek_elteres = 0
        self.talalatok = 0
        self.jaror_cel_kordinata = None
        self.alapot = "jarorozes"
        self.jarorozes_figyelo = {"kordinata": None, "ido": 0.0, "jelenleg": 0}
        self.dontes_fazis = 0
        self.dontes_gyakorisag = beallitasok.dontes_gyakorisag
        self.dontes_idozito = 0
        self.buff_gyujto = {} #{delta ido, cel ido, buff definicio, ertek, buff neve, buff fajtaja, el = True/False}
        self.uj_buffok = {} # buff neve : [cél idő, ertek, meddig lesz a buff érvényes]
        self.buff_gyujto_torlo_lista = []
        self.buff_kijelzes_felszedeskor_ido = beallitasok.buff_kijelzes_felszedeskor_ido
        self.pajzs = 1.0
        self.alap_pajzs = 1.0

    def tuzeles(self, delta_ido):
        self.loves_idozito += delta_ido
        if self.loves_idozito >= self.loves_cooldown and self.loves:
            self.loves_idozito = 0
            self.loves = False
            return True
        return False

    def allapot_dict(self):
        alapot = {
            "azonosito": self.azonosito,
            "nev": self.nev,
            "szin": self.szin,
            "x": self.x,
            "y": self.y,
            "sugar": self.sugar,
            "hp": self.hp,
            "el": self.el,
            "eltelt_ido": self.eltelt_ido,
            "fok": self.fok,
            "kep": self.tank_kep_nev,
            "olesek": self.olesek,
            "pontok": self.talalatok,
            "max_hp": self.alap_hp,
            "tuzelt": self.tuzelt,
            "uj_buffok": self.uj_buffok,

            "buffok": [
                {
                    "nev": buff["buff_nev"],
                    "ertek": buff["ertek"],
                    "eltelt_ido": buff["delta_ido"],
                    "cel_ido": buff["cel_ido"],
                }
                for buff in self.buff_gyujto.values() if buff.get("el", True) and buff.get("cel_ido", 0) > 0
            ],
        }
        self.tuzelt = False
        self.uj_buffok = {}
        return alapot
    
    def buff_kezelo(self, delta_ido):
        torlendo = []

        for kulcs, buff in self.buff_gyujto.items():
            buff["delta_ido"] += delta_ido

            if buff["delta_ido"] >= buff["cel_ido"]:
                buff["buff_definicio"](self, buff["ertek"], vissza_allitas=True)
                torlendo.append(kulcs)

        for kulcs in torlendo:
            del self.buff_gyujto[kulcs]


    def buff_hozzaadasa(self, buff_nev, buff_definicio, ertek=None, cel_ido=None):
        if not cel_ido or cel_ido <= 0:
            buff_definicio(self, ertek)
            self.uj_buffok[buff_nev] = [self.buff_kijelzes_felszedeskor_ido, ertek, None]
            return

        
        kulcs = buff_nev[:-1] if buff_nev.endswith(("+", "-")) else buff_nev

        regi_buff = self.buff_gyujto.get(kulcs)

        if regi_buff is not None:
            regi_buff["buff_definicio"](self, regi_buff["ertek"], vissza_allitas=True)

        
        buff_definicio(self, ertek)
        self.uj_buffok[buff_nev] = [self.buff_kijelzes_felszedeskor_ido, ertek, cel_ido]

        self.buff_gyujto[kulcs] = {
            "delta_ido": 0.0,
            "cel_ido": cel_ido,
            "buff_definicio": buff_definicio,
            "ertek": ertek,
            "buff_nev": buff_nev,
            "el": True,
        }
        
class Buffok:
    @staticmethod
    def hp(self, hp, vissza_allitas=False):
        self.hp += hp * self.pajzs
        self.hp = round(self.hp, 2)
        if self.hp <= 0:
            self.el = False
        
    @staticmethod
    def shild(self, vedes, vissza_allitas=False):
        if vissza_allitas:
            self.pajzs = self.alap_pajzs
            return
        self.pajzs = vedes
    @staticmethod
    def speed(self, sebesseg, vissza_allitas=False):
        if vissza_allitas:
            self.sebesseg = self.alap_sebesseg
            return
        self.sebesseg = self.alap_sebesseg + sebesseg
    
    @staticmethod
    def bulet(self, coldown, vissza_allitas=False):
        if vissza_allitas:
            self.loves_cooldown = self.loves_cooldown_alap
            return
        self.loves_cooldown = coldown

    @staticmethod
    def rotate(self, sebesseg,  vissza_allitas=False):
        if vissza_allitas:
            self.fordulasi_sebesseg = self.fordulasi_sebesseg_alap
            return
        self.fordulasi_sebesseg = sebesseg

    @staticmethod
    def kill(self, oles, vissza_allitas=False):
        if vissza_allitas:
            self.olesek -= self.olesek_elteres
            self.olesek_elteres = 0
        self.olesek += oles
        self.olesek_elteres += 1

    @staticmethod
    def teleport(self, vilag, vissza_allitas=False):
        self.x, self.y = vilag._tankos_spawn_pozicio()

class Platform:
    def __init__(self, x, y, sebzes=0, fajta="alap"):
        pass

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, masik):
        return Vector(self.x + masik.x, self.y + masik.y)

    def __sub__(self, masik):
        return Vector(self.x - masik.x, self.y - masik.y)

    def __mul__(self, szam):
        return Vector(self.x * szam, self.y * szam)

    def __iadd__(self, masik):
        self.x += masik.x
        self.y += masik.y
        return self

    def __getitem__(self, index):
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError("A vector indexe csak 0 vagy 1 lehet!")

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
class P_elolenyek:
    def __init__(self, azonosito: str, nev: str, x: float, y: float, sugar, k_magassag: int, k_szelleseg: int, beallitasok: Beallitasok, fajta:str):
        self.azonosito = azonosito
        self.nev = nev 
        self.x = x 
        self.y = y 
        self.sugar = sugar
        self.width = 40
        self.height = 50
        self.sebesseg = beallitasok.jatekos_sebesseg
        self.alap_sebesseg = self.sebesseg
        self.fajta = fajta
        self.alap_hp = float(beallitasok.jatekos_hp)
        self.hp = self.alap_hp
        self.tamadas_szelesseg = 40
        self.tamadas_magassag = 30
        self.el = True 
        self.tamadas_sebzes = 1
        self.mozog_balra = False 
        self.mozog_jobbra = False 
        self.mozog_fel = False
        self.mozog_le = False 
        self.utes = False
        self.tuzelt = False
        self.jump = False
        self.attack = False
        self.utes_cooldown = beallitasok.utes_cooldown
        self.utes_idozito = beallitasok.utes_cooldown -0.3
        self.utes_cooldown_alap = self.utes_cooldown-0.5
        self.eltelt_ido = 0.0
        self.utolso_racs = None
        self.jatekos_e = False
        self.gondolkozasi_ido = 5
        self.tamadas_id = 0
        
        self.olesek = 0
        self.talalatok = 0
        self.dontes_fazis = 0
        self.dontes_gyakorisag = beallitasok.dontes_gyakorisag
        self.dontes_idozito = 0
        self.buff_gyujto = {} #{delta ido, cel ido, buff definicio, ertek, buff neve, buff fajtaja, el = True/False}
        self.uj_buffok = {} # buff neve : [cél idő, ertek, meddig lesz a buff érvényes]
        self.buff_gyujto_torlo_lista = []
        self.buff_kijelzes_felszedeskor_ido = beallitasok.buff_kijelzes_felszedeskor_ido
        self.pajzs = 1.0
        self.alap_pajzs = 1.0
        self.jumping = 0
        self.jumping_szamlalo = 0
        self.dare_i_jump = True
        self.can_i_jump = False
        self.irany = 0 # 0=elsö nezet állás, 1 jobbra oldalso nezet, 2 balra oldalsonezet, 3 fel első nézet, 4 le also nezet
        self.attack_rect = None

        #['Dying', 'Falling Down', 'Hurt', 'Idle', 'Idle Blinking', 'Jump Loop', 'Jump Start', 'Kicking', 'Run Slashing', 'Run Throwing',
        #'Running', 'Slashing', 'Slashing in The Air', 'Sliding', 'Throwing', 'Throwing in The Air', 'Walking']
        self.akcio = "Idle"
        self.irany = 1
        self.kamera  = None
        self.k_szelesseg = k_szelleseg #screen width
        self.k_magassag = k_magassag

        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)

    def tamadas(self, delta_ido):
            self.utes_idozito += delta_ido
            if self.utes_idozito >= self.utes_cooldown and self.utes:
                self.utes_idozito = 0
                self.utes = False
                return True
            return False

    def allapot_dict(self):
        alapot = {
            "azonosito": self.azonosito,
            "nev": self.nev,
            "x": self.x,
            "y": self.y,
            "kep": self.fajta,

            "width": self.width,
            "height": self.height,
            "sugar": self.sugar,
            "irany": self.irany,
            "hp": self.hp,
            "el": self.el,
            "eltelt_ido": self.eltelt_ido,
            "tamadas_id": self.tamadas_id,

            "eltelt_ido": self.eltelt_ido,
            "olesek": self.olesek,
            "pontok": self.talalatok,
            "max_hp": self.alap_hp, 
            "uj_buffok": self.uj_buffok,
            "akcio": self.akcio,
            "irany": self.irany,
            "fel": self.mozog_fel,
            "le": self.mozog_le,
            "attack": self.attack,

            "buffok": [
                {
                    "nev": buff["buff_nev"],
                    "ertek": buff["ertek"],
                    "eltelt_ido": buff["delta_ido"],
                    "cel_ido": buff["cel_ido"],
                }
                for buff in self.buff_gyujto.values() if buff.get("el", True) and buff.get("cel_ido", 0) > 0
            ],
        }
        
        self.uj_buffok = {}
        return alapot
    
    def buff_kezelo(self, delta_ido):
        torlendo = []

        for kulcs, buff in self.buff_gyujto.items():
            buff["delta_ido"] += delta_ido

            if buff["delta_ido"] >= buff["cel_ido"]:
                buff["buff_definicio"](self, buff["ertek"], vissza_allitas=True)
                torlendo.append(kulcs)

        for kulcs in torlendo:
            del self.buff_gyujto[kulcs]


    def buff_hozzaadasa(self, buff_nev, buff_definicio, ertek=None, cel_ido=None):
        if not cel_ido or cel_ido <= 0:
            buff_definicio(self, ertek)
            self.uj_buffok[buff_nev] = [self.buff_kijelzes_felszedeskor_ido, ertek, None]
            return

        
        kulcs = buff_nev[:-1] if buff_nev.endswith(("+", "-")) else buff_nev

        regi_buff = self.buff_gyujto.get(kulcs)

        if regi_buff is not None:
            regi_buff["buff_definicio"](self, regi_buff["ertek"], vissza_allitas=True)

        
        buff_definicio(self, ertek)
        self.uj_buffok[buff_nev] = [self.buff_kijelzes_felszedeskor_ido, ertek, cel_ido]

        self.buff_gyujto[kulcs] = {
            "delta_ido": 0.0,
            "cel_ido": cel_ido,
            "buff_definicio": buff_definicio,
            "ertek": ertek,
            "buff_nev": buff_nev,
            "el": True,
        }
        
class Kamera:
    def __init__(self, kepernyo_szelesseg, kepernyo_magassag):
        self.x = 0
        self.y = 0
        self.kepernyo_szelesseg = kepernyo_szelesseg
        self.kepernyo_magassag = kepernyo_magassag

        
        self.holtter_szelesseg = 50  
        self.holtter_magassag = 50 
        
       
        self.fokusz_x = 0
        self.fokusz_y = 0
        self.elso_frissites = True   
        
        self.kovetes_sebesseg_x = 0.08
        self.kovetes_sebesseg_y = 0.2
        self.eloretekintes_tavolsag = 0#150
        self.jelenlegi_eloretekintes = 0

    def mozgas(self, jatekos_x, jatekos_y, jatekos_szelesseg, jatekos_magassag, irany):
        # A játékos tényleges közepe
        jatekos_kozep_x = jatekos_x + (jatekos_szelesseg / 2) + self.kepernyo_szelesseg / 2
        jatekos_kozep_y = jatekos_y + (jatekos_magassag / 2) + self.kepernyo_magassag / 2
        
        
        if self.elso_frissites:
            self.fokusz_x = jatekos_kozep_x
            self.fokusz_y = jatekos_kozep_y
            self.elso_frissites = False

        
        bal_hatar = self.fokusz_x - (self.holtter_szelesseg / 2)
        jobb_hatar = self.fokusz_x + (self.holtter_szelesseg / 2)
        
        if jatekos_kozep_x < bal_hatar:
            self.fokusz_x -= (bal_hatar - jatekos_kozep_x) 
        elif jatekos_kozep_x > jobb_hatar:
            self.fokusz_x += (jatekos_kozep_x - jobb_hatar) 
            
        
        felso_hatar = self.fokusz_y - (self.holtter_magassag / 2)
        also_hatar = self.fokusz_y + (self.holtter_magassag / 2)
        
        if jatekos_kozep_y < felso_hatar:
            self.fokusz_y -= (felso_hatar - jatekos_kozep_y)
        elif jatekos_kozep_y > also_hatar:
            self.fokusz_y += (jatekos_kozep_y - also_hatar)

        
        cel_eloretekintes = irany * self.eloretekintes_tavolsag
        self.jelenlegi_eloretekintes += (cel_eloretekintes - self.jelenlegi_eloretekintes) * 0.05
        
       
        cel_kamera_x = (self.fokusz_x - self.kepernyo_szelesseg / 2) + self.jelenlegi_eloretekintes
        cel_kamera_y = (self.fokusz_y - self.kepernyo_magassag / 2)

        
        self.x += (cel_kamera_x - self.x) * self.kovetes_sebesseg_x
        self.y += (cel_kamera_y - self.y) * self.kovetes_sebesseg_y


    def apply(self):
        return self.x, self.y


class Lovedek:
    def __init__(self, azonosito, tulajdonos_id, x, y, irany_x, irany_y):
        self.azonosito = azonosito
        self.tulajdonos_id = tulajdonos_id
        self.x = x
        self.y = y
        self.irany_x = irany_x
        self.irany_y = irany_y
        self.sebesseg = 700
        self.sugar = 6
        self.sebzes = 10
        self.patanas_db = 0.0
        self.max_patanas = 1.0
        self.utolso_racs = None
        self.el = True

    def mozgas(self, delta_ido, jarhato):
        uj_x = self.x + self.irany_x * self.sebesseg * delta_ido
        uj_y = self.y + self.irany_y * self.sebesseg * delta_ido

        if jarhato(uj_x, self.y, self.sugar):
            self.x = uj_x
        else:
            self.irany_x *= -1
            self.patanas_db += 1

        if jarhato(self.x, uj_y, self.sugar):
            self.y = uj_y
        else:
            self.irany_y *= -1
            self.patanas_db += 1

        if self.patanas_db >= self.max_patanas:
            self.el = False
        
    
    def allapot_dict(self):
        return {
            "azonosito": self.azonosito,
            "x": self.x,
            "y": self.y,
            "sugar": self.sugar,
        }

class KigyoAdat:
    def __init__(self, azonosito: str, nev: str, szin: Tuple[int, int, int], nehezseg_szint: str, fej_x: float, fej_y: float, beallitasok: Beallitasok, jatekos_e: bool = False):
        self.azonosito = azonosito 
        self.nev = nev 
        self.szin = szin  
        self.fej_szin = SzinSeged.fej_szin(szin) 
        self.nehezseg_szint = nehezseg_szint 
        self.jatekos_e = jatekos_e 
        self.el = True 
        self.olesek = 0
        self.alma_pontok = 0
        self.sugar = beallitasok.kigyó_sugár
        self.resz_tav = beallitasok.kigyo_resz_tav
        self.irany_x = 1.0
        self.irany_y = 0.0 
        self.alap_sebesseg = 7.0 
        self.sebesseg = 7.0
        self.cel_sebesseg = 7.0 
        self.no = beallitasok.kigyo_no 
        self.nosz = 0 
        if not jatekos_e and beallitasok.kezdes:
            self.nosz = random.randint(5, 200)
        self.osztas = 2 
        self.aktualis_osztas = 2.0
        self.idealis_tavolsag = float(self.resz_tav)
        self.utvonal = []
        self.test_pontok = [] 
        self.dontes_idozito = 0 
        self.dontes_gyakorisag = beallitasok.dontes_gyakorisag 
        self.allapot = "vadaszat"
        self.celpont = None
        self.csapda_mod = False
        self.szerep = "uldozo" 
        self.gyorsit = False 
        self.utolso_racs = []
        self.dontes_fazis = 0
        self.beallitasok = beallitasok
        self.vesztes_testhosz_szamulo = 0
        self.eltelt_ido = 0
        

        self._nehezseg_beallitas(nehezseg_szint)
        self._letrehoz_indulo_test(fej_x, fej_y, beallitasok)
        self.novekedes(self.beallitasok)
    
    def hosz_vesztes(self):
        if self.gyorsit:
            self.alma_pontok -= 1
            self.nosz -= self.beallitasok.kigyo_novekedes_alma_db
            cel_hossz = self.beallitasok.kigyo_alap_hossz + (self.nosz // self.no)
            while len(self.test_pontok) > cel_hossz:
                del self.test_pontok[-1]
            return True

    def _nehezseg_beallitas(self, nehezseg_szint) :
        if nehezseg_szint == "Easy":
            self.alap_sebesseg = 5.0 * self.beallitasok.fps
        elif nehezseg_szint == "Normal":
            self.alap_sebesseg = 7.0 * self.beallitasok.fps
        elif nehezseg_szint == "Hard":
            self.alap_sebesseg = 9.0 * self.beallitasok.fps
        elif nehezseg_szint == "Nightmare":
            self.alap_sebesseg = 12.0 * self.beallitasok.fps
        elif nehezseg_szint == "Hell":
            self.alap_sebesseg = 15.0 * self.beallitasok.fps
        else:
            self.alap_sebesseg = 7.0 * self.beallitasok.fps

        self.sebesseg = self.alap_sebesseg
        self.cel_sebesseg = self.alap_sebesseg
        self.idealis_tavolsag = max(float(self.resz_tav), self.sugar * 1.4)
        self.osztas = max(1, round(self.idealis_tavolsag / max(1.0, self.alap_sebesseg)))
        self.aktualis_osztas = float(self.osztas)

    def _letrehoz_indulo_test(self, fej_x: float, fej_y: float, beallitasok: Beallitasok) :
        self.test_pontok = []
        if self.jatekos_e:
            for index in range(beallitasok.kigyo_alap_hossz):
                self.test_pontok.append([fej_x - index * self.idealis_tavolsag, fej_y])
        else:
            for index in range(beallitasok.kigyo_alap_hossz):
                self.test_pontok.append([fej_x - index * self.idealis_tavolsag, fej_y])
        self.utvonal = [list(self.test_pontok[0])]

    def novekedes(self, beallitasok: Beallitasok) :
        self.nosz += beallitasok.kigyo_novekedes_alma_db
        cel_hossz = beallitasok.kigyo_alap_hossz + (self.nosz // self.no)
        while len(self.test_pontok) < cel_hossz:
            utolso_x, utolso_y = self.test_pontok[-1]
            self.test_pontok.append([utolso_x, utolso_y])

    def beallit_irany(self, dx, dy) :
        ndx, ndy = KorSeged.normalizal(dx, dy)
        if abs(ndx) > 1e-6 or abs(ndy) > 1e-6:
            self.irany_x = ndx
            self.irany_y = ndy

    def fej_pozicio(self):
        return self.test_pontok[0][0], self.test_pontok[0][1]

    def allapot_dict(self, kamera_x = None, kamera_y = None, szelesseg = None, magassag = None, puffer = 100.0, pont_limit = None):
        pontok = self.test_pontok
        if kamera_x is not None and kamera_y is not None and szelesseg is not None and magassag is not None:
            bal = kamera_x - puffer
            jobb = kamera_x + szelesseg + puffer
            fent = kamera_y - puffer
            lent = kamera_y + magassag + puffer
            pontok = [pont for pont in self.test_pontok if bal < pont[0] < jobb and fent < pont[1] < lent]
            if not pontok and self.test_pontok:
                pontok = [self.test_pontok[0]]
        if pont_limit is not None:
            pontok = pontok[:pont_limit]
        return {
            "azonosito": self.azonosito,
            "nev": self.nev,
            "szin": self.szin,
            "fej_szin": self.fej_szin,
            "test_pontok": pontok,
            "el": self.el,
            "olesek": self.olesek,
            "pontok": self.alma_pontok,
            "sugar": self.sugar,
            "jatekos_e": self.jatekos_e,
            "ossz_testhosz": len(self.test_pontok),
            "eltelt_ido": self.eltelt_ido
        }

    def allapot_dict_kicsi(self):
        fej_x, fej_y = self.fej_pozicio()

        return {
            "azonosito": self.azonosito,
            "fej_x": fej_x,
            "fej_y": fej_y,
            "irany_x": self.irany_x,
            "irany_y": self.irany_y,
            "sebesseg": self.sebesseg,
            "ossz_testhosz": len(self.test_pontok),
            "el": self.el,
        }

class Tank_Terkep:

    """
     1 = fal
     0 = járható padló
     2 = víz (járható)
    -1 = kijárat (lépcső / vissza a kastélyba)
     3 = repedezett fal (NEM járható)
     4 = lyuk a falban (JÁRHATÓ)
    """

    def __init__(self, vilag, szel=500, mag=500, cella=80, seed=None, rooms_target=None, beallitasok = Beallitasok()):
        self.SZEL = int(szel)
        self.MAG = int(mag)
        self.CELLA = int(cella)
        self.beallitasok = beallitasok
        self.vilag = vilag

        self.chest_azonosito = 0

        self.chest_racs = defaultdict(set)

        if seed is None:
            seed = random.randrange(1 << 30)
        self.seed = int(seed)
        self.rng = random.Random(self.seed)

        self.racs = np.ones((self.MAG, self.SZEL), dtype=np.int8)

        self.szinek = {
            1: "#1a1a1a",   # fal
            0: "#c9b37e",   # padló
            2: "#0043ec",   # víz
            -1: "#1100ff",  # kijárat
            3: "#464040",   # repedes_fal
            4: "#692F28",   # lyuk_fal 
        } 
        self.rooms = []


        def carve_rect(s1, o1, s2, o2, val=0):
            r1 = max(0, min(self.MAG - 1, int(s1)))
            c1 = max(0, min(self.SZEL - 1, int(o1)))
            r2 = max(0, min(self.MAG - 1, int(s2)))
            c2 = max(0, min(self.SZEL - 1, int(o2)))
            if r2 < r1: r1, r2 = r2, r1
            if c2 < c1: c1, c2 = c2, c1
            
            self.racs[r1:r2+1, c1:c2+1] = val

        def room_center(room):
            s1, o1, s2, o2 = room
            return (s1 + s2) // 2, (o1 + o2) // 2

        def overlaps(a, b, pad=2):
            a1, a2, a3, a4 = a
            b1, b2, b3, b4 = b
            return not (a3 + pad < b1 or b3 + pad < a1 or a4 + pad < b2 or b4 + pad < a2)

        
        generalas_cfg = {}
        fajl = os.path.join(os.path.dirname(__file__), "terkep.json")
        if os.path.exists(fajl):
            with open(fajl, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            generalas_cfg = (cfg.get("vilagok", {}) or {}).get("tankos", {}).get("generalas", {}) or {}
        

        folyosomin = int(generalas_cfg.get("folyoso_min_szelesseg", 1))
        folyosomax = int(generalas_cfg.get("folyoso_max_szelesseg", 4))
        zsakutca_db = int(generalas_cfg.get("zsakutcak", 120))

        folyosomin = max(1,  folyosomin)
        folyosomax = max(folyosomin, folyosomax)
        zsakutca_db = max(10, zsakutca_db)

        def _farag_pont(s, o, szelesseg):
            w = max(1, int(szelesseg))
            r = w // 2
            carve_rect(s - r, o - r, s + r, o + r, 0)

        def alagut_random_walk(s0, o0, s1, o1, szel_min, szel_max):
            s, o = int(s0), int(o0)
            cel_s, cel_o = int(s1), int(o1)
            szel = self.rng.randint(szel_min, szel_max)
            max_lepes = max(2000, (abs(cel_s - s) + abs(cel_o - o)) * 15)
            
            for _ in range(max_lepes):
                _farag_pont(s, o, szel)
                if s == cel_s and o == cel_o:
                    break

                if self.rng.random() < 0.22:
                    szel += self.rng.choice([-1, 1])
                    szel = max(szel_min, min(szel_max, szel))

                ds = cel_s - s
                do = cel_o - o
                iranyok = []
                
                if self.rng.random() < 0.70:
                    if abs(ds) >= abs(do):
                        iranyok.append((1 if ds > 0 else -1, 0))
                        if do != 0: iranyok.append((0, 1 if do > 0 else -1))
                    else:
                        iranyok.append((0, 1 if do > 0 else -1))
                        if ds != 0: iranyok.append((1 if ds > 0 else -1, 0))
                    iranyok += self.rng.sample([(0, 1), (0, -1), (1, 0), (-1, 0)], k=2)
                else:
                    iranyok = self.rng.sample([(0, 1), (0, -1), (1, 0), (-1, 0)], k=4)

                lepett = False
                for d_s, d_o in iranyok:
                    ns, no = s + d_s, o + d_o
                    if 1 <= ns < self.MAG - 1 and 1 <= no < self.SZEL - 1:
                        s, o = ns, no
                        lepett = True
                        break
                if not lepett:
                    break

            _farag_pont(cel_s, cel_o, szel)

        def _szoba_kapcsolatok_ket_utas():
            kapcsolatok = set()
            def _osszekot(i, j):
                if i == j: return
                a, b = min(i, j), max(i, j)
                if (a, b) in kapcsolatok: return
                kapcsolatok.add((a, b))
                s0, o0 = room_center(self.rooms[i])
                s1, o1 = room_center(self.rooms[j])
                alagut_random_walk(s0, o0, s1, o1, folyosomin, folyosomax)

            for i in range(1, len(self.rooms)):
                s0, o0 = room_center(self.rooms[i])
                tavok = []
                for j in range(len(self.rooms)):
                    if i == j: continue
                    s1, o1 = room_center(self.rooms[j])
                    d = abs(s0 - s1) + abs(o0 - o1)
                    tavok.append((d, j))
                tavok.sort(key=lambda t: t[0])
                if tavok:
                    _osszekot(i, tavok[0][1])
                if len(tavok) > 1 and self.rng.random() < 0.75:
                    _osszekot(i, tavok[1][1])

            extra = max(6, len(self.rooms) // 5)
            for _ in range(extra):
                a = self.rng.randrange(len(self.rooms))
                b = self.rng.randrange(len(self.rooms))
                _osszekot(a, b)

        def _zsakutcak_hozzaadasa(db):
            yy, xx = np.where(self.racs[2:self.MAG-2, 2:self.SZEL-2] == 0)
            padlok = list(zip(yy + 2, xx + 2))
            
            if not padlok: return

            def fal_szomszedok(s, o):
                ir = []
                for ds, do in [(1,0),(-1,0),(0,1),(0,-1)]:
                    ns, no = s+ds, o+do
                    if 1 <= ns < self.MAG-1 and 1 <= no < self.SZEL-1 and self.racs[ns, no] == 1:
                        ir.append((ds, do))
                return ir

            probalkozas = 0
            max_probalkozas = db * 8
            kesz = 0
            while kesz < db and probalkozas < max_probalkozas:
                probalkozas += 1
                s, o = padlok[self.rng.randrange(len(padlok))]
                iranyok = fal_szomszedok(s, o)
                if not iranyok: continue
                ds, do = iranyok[self.rng.randrange(len(iranyok))]

                hossz = self.rng.randint(8, 55)
                szel = self.rng.randint(folyosomin, folyosomax)

                cs_s, cs_o = s, o
                sikerult = False
                for _ in range(hossz):
                    ns, no = cs_s + ds, cs_o + do
                    if not (2 <= ns < self.MAG - 2 and 2 <= no < self.SZEL - 2):
                        break

                    if self.racs[ns, no] == 0:
                        break

                    _farag_pont(ns, no, szel)
                    cs_s, cs_o = ns, no
                    sikerult = True

                    if self.rng.random() < 0.25:
                        szel = max(folyosomin, min(folyosomax, szel + self.rng.choice([-1, 1])))

                    if self.rng.random() < 0.22:
                        if (ds, do) in [(1,0),(-1,0)]: ds, do = (0, self.rng.choice([-1, 1]))
                        else: ds, do = (self.rng.choice([-1, 1]), 0)

                if sikerult:
                    kesz += 1

        
        start_room = (1, 1, 20, 20)
        carve_rect(*start_room, val=0)
        self.rooms.append(start_room)
        

        
        target = int(rooms_target) if rooms_target is not None else self.rng.randint(24, 40)
        attempts = target * 25
        for _ in range(attempts):
            if len(self.rooms) >= target: break
            h, w = self.rng.randint(6, 18), self.rng.randint(6, 18)
            s1 = self.rng.randint(2, self.MAG - h - 3)
            o1 = self.rng.randint(2, self.SZEL - w - 3)
            room = (s1, o1, s1 + h, o1 + w)
            if any(overlaps(room, r, pad=2) for r in self.rooms):
                continue
            carve_rect(*room, val=0)
            self.rooms.append(room)

       
        _szoba_kapcsolatok_ket_utas()

        _zsakutcak_hozzaadasa(zsakutca_db)

        for room in self.rooms[1:]:
            if self.rng.random() < 0.20:
                s1, o1, s2, o2 = room
                if (s2 - s1) >= 10 and (o2 - o1) >= 10:
                    ph, pw = self.rng.randint(3, 6), self.rng.randint(3, 6)
                    ps = self.rng.randint(s1 + 2, s2 - ph - 2)
                    po = self.rng.randint(o1 + 2, o2 - pw - 2)
                    carve_rect(ps, po, ps + ph, po + pw, val=2)

        
        for i in range(generalas_cfg.get("chest_kezdo_db", 0)):
            self.chest_generalas(i)

        es, eo = room_center(self.rooms[-1])
        self.racs[es, eo] = -1

        self.racs[0, :] = 1
        self.racs[-1, :] = 1
        self.racs[:, 0] = 1
        self.racs[:, -1] = 1

        self.racs[2, 2] = 0

    def chest_generalas(self, azonosito):
        def _jarhato_tile(v):
            # 0: padló, 2: víz, -1: kijárat, 4: lyuk_fal
            return v in (0, 2, -1, 4)

        
        for _ in range(5000):  
            y = self.rng.randint(2, self.MAG - 3)
            x = self.rng.randint(2, self.SZEL - 3)

            
            if self.racs[y, x] != 1:
                continue

            fel = self.racs[y-1, x]
            le = self.racs[y+1, x]
            bal = self.racs[y, x-1]
            jobb = self.racs[y, x+1]

            
            if ((_jarhato_tile(bal) and _jarhato_tile(jobb)) or (_jarhato_tile(fel) and _jarhato_tile(le))):
                if self.rng.random() < 0.004:  # lyuk_esely
                    self.racs[y, x] = 4  # lyuk_fal
                    continue

            
            if (_jarhato_tile(fel) or _jarhato_tile(le) or _jarhato_tile(bal) or _jarhato_tile(jobb)):
                self.racs[y, x] = 3  # repedes_fal
                chest = Chest(azonosito, x * self.CELLA + self.CELLA/2, y * self.CELLA + self.CELLA/2, self.beallitasok, x, y, self.vilag)
                hely = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, x*self.CELLA, y*self.CELLA)
                self.chest_racs[hely[0], hely[1]].add(chest)
                return chest

        
        for y in range(2, self.MAG - 2):
            for x in range(2, self.SZEL - 2):
                if self.racs[y, x] == 1:
                    fel, le, bal, jobb = self.racs[y-1, x], self.racs[y+1, x], self.racs[y, x-1], self.racs[y, x+1]
                    if (_jarhato_tile(fel) or _jarhato_tile(le) or _jarhato_tile(bal) or _jarhato_tile(jobb)):
                        self.racs[y, x] = 3
                        chest = Chest(azonosito, x * self.CELLA + self.CELLA/2, y * self.CELLA + self.CELLA/2, self.beallitasok, x, y, self.vilag)
                        hely = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, x*self.CELLA, y*self.CELLA)
                        self.chest_racs[hely[0], hely[1]].add(chest)
                        return chest
                    

    def adott_cella_ertek_atiras(self, cellax, cellay, ertek):
        self.racs[int(cellay), int(cellax)] = ertek

        

    def jarhato(self, sor, oszlop):
        if not (0 <= sor < self.MAG and 0 <= oszlop < self.SZEL):
            return False
        
        v = self.racs[sor, oszlop]
        
        
        if v == 1 or v == 3:
            return False
            
        return True

    def csempe_hely(self, x, y):
        oszlop = int(x // self.CELLA)
        sor = int(y // self.CELLA)
        return oszlop, sor

class VilagAllapot:
    BEALITASOK = Beallitasok()
    def __init__(self, beallitasok: Optional[Beallitasok] = None, jatek_mode: str = "alma", nehezseg_szint: str = "Normal", vilag_szelesseg=None, vilag_magassag=None, ai_db=6):
        self.beallitasok = beallitasok or Beallitasok() 
        self.jatek_mode = jatek_mode 
        self.nehezseg_szint = nehezseg_szint 
        self.racs_vilag_alma: Dict[Tuple[int, int], List[Tuple[float, float]]] = defaultdict(list) 
        self.racs_vilag_kigyo: Dict[Tuple[int, int], List[Tuple[str, int, float, float, float]]] = defaultdict(list)
        self.racs_vilag_lovedekek = defaultdict(set)
        self.racs_vilag_tank_jatekosok = defaultdict(set)
        self.racs_vilag_chest = defaultdict(set)
        self.racs_vilag_chestdrop = defaultdict(set)
        self.jatekosok: Dict[str, object] = {} 
        self.kigyo_ellenseg: List[KigyoAdat] = []
        self.tank_ellensegek: List[Tanki] = []
        self.max_kigyok = 0 
        self.eddigi_kigyok = 0 
        self.eddigi_tankok_npc = 0
        self.kigyo_respawn_idozito = 0 
        self.alma_potlasi_idozito = 0 
        self.veletlen = random.Random() 
        self.dontes_kiosztas = 0
        self.frissitesi_szamlalo = 0
        self.max_frisitesi_szamolo = self.beallitasok.dontes_gyakorisag
        self.terkep_tank = None
        self.lovedekek = []
        self.lovedek_azonosito = 0
        self.halal_lista = []
        self.kamera_sugar = float
        self.tank_szeleseg = vilag_szelesseg or beallitasok.tank_vilag_szelesseg
        self.tank_magassag = vilag_magassag or beallitasok.tank_vilag_magassag
        self.ai_db = int(ai_db)
        self.acc = 0.5
        self.gyorsulas_csokentes = self.beallitasok.gyorsulas_csokentes
        self.gravitacio = self.beallitasok.gravitacio
        self.alap_gravitacio = self.gravitacio
        self.max_gravitacio = self.beallitasok.max_gravitacio
        
        
        self.vilag_terkep_bealitasok = {}
        fajl = os.path.join(os.path.dirname(__file__), "terkep.json")
        if os.path.exists(fajl):
            with open(fajl, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.vilag_terkep_bealitasok = (cfg.get("vilagok", {})) or {}

        self.max_chest = self.vilag_terkep_bealitasok.get("tankos", {}).get("generalas", {}).get("chest_max_db", 10)
        self.aktualis_chest_db = self.vilag_terkep_bealitasok.get("tankos", {}).get("generalas", {}).get("chest_kezdo_db", 10)
        self.chest_azonosito = self.aktualis_chest_db-1
        self.chestek = []
        self.uj_jatek(jatek_mode, nehezseg_szint)
        

    def frissites(self, delta_ido) :
        if self.jatek_mode == "alma":
            self._alma_mod_frissites(delta_ido)
            self.beallitasok.kezdes = False
        elif self.jatek_mode == "tankos":
            self._tankos_mod_frissites(delta_ido)
        elif self.jatek_mode == "platformer":
            self._platformer_frissites(delta_ido)

        else:
            print(f"ilyen mode nincs: {self.jatek_mode}")
            return

    def uj_jatek(self, jatek_mode, nehezseg_szint, platformer_jelenlegi_szoba="") :
        self.jatek_mode = jatek_mode
        self.nehezseg_szint = nehezseg_szint
        self.racs_vilag_alma.clear()
        self.racs_vilag_kigyo.clear()
        self.jatekosok = {}
        self.kigyo_ellenseg = []
        self.eddigi_kigyok = 0
        self.kigyo_respawn_idozito = 0
        self.alma_potlasi_idozito = 0
        self.max_kigyok = self.kigyo_celszam(nehezseg_szint)
        if self.jatek_mode == "alma":
            self._almak_generalasa(self._kezdo_alma_db())
            self._ai_kigyok_potlas(self.max_kigyok)
        elif self.jatek_mode == "tankos":
            self.tankos_kezdes()
        elif self.jatek_mode == "platformer":
            self.platformer_kezdes(platformer_jelenlegi_szoba)

        else:
            print(f"nincs ilyen játékmood: {self.jatek_mode}")
            return

    def jatekos_hozzaadasa(self, azonosito, nev, szin, kep=None, sugar=10, k_szeleseg=600, k_magassag=400):
        if self.jatek_mode == "alma":
            x, y = self._szoba_pozicio_biztonsagos(self.beallitasok.kigyó_sugár, "kigyo")
            uj = KigyoAdat(azonosito, nev, szin, self.nehezseg_szint, x, y, self.beallitasok, True)
            self.jatekosok[azonosito] = uj
            self.racs_kigyo_hozzaad(uj)
        elif self.jatek_mode == "tankos":
            x, y = self._tankos_spawn_pozicio()
            uj = Tanki(azonosito, nev, szin, x, y, self.beallitasok)
            uj.jatekos_e = True
            #uj.loves_cooldown = 0.1
            #uj.sebesseg = 500
            uj.hp = 100
            uj.buff_hozzaadasa("shild", Buffok.shild, 0.0, 30)
            if kep is not None:
                uj.tank_kep_nev = kep
            self.jatekosok[azonosito] = uj
            self.tank_jatekos_racs_hozzaad(uj)
        elif self.jatek_mode == "platformer":
            x, y = self.platformer_spawn_kereses(40, 50)
            for i in range(2):
                uj = P_elolenyek(azonosito, nev, x, y, sugar, k_szeleseg, k_magassag, self.beallitasok, kep)
                uj.kamera = Kamera(400, 400) #uj.x, uj.y, k_szeleseg, k_magassag)
                self.jatekosok[azonosito] = uj

    def jatekos_torlese(self, azonosito: str) :
        jatekos = self.jatekosok.get(azonosito)

        if isinstance(jatekos, KigyoAdat):
            self._kigyo_racsbol_torles(jatekos)
            if azonosito in self.jatekosok:
                self.kigyo_to_almak([self.jatekosok[azonosito]])
                del self.jatekosok[azonosito]
        elif isinstance(jatekos, Tanki):
            self.tank_jatekos_racsbol_torles(jatekos)
            del self.jatekosok[azonosito]
        elif isinstance(jatekos, P_elolenyek):
            del self.jatekosok[azonosito]


    def folytatas(self, adatok):
        if isinstance(adatok, tuple):
            azonosito, nev, szin, kep = adatok
            #if azonosito not in self.jatekosok:
            #   return
            try:
                self.jatekos_torlese(azonosito)
            except:
                pass
            self.jatekos_hozzaadasa(azonosito, nev, szin, kep)
            
        else:
            azonosito = adatok.azonosito
            nev = adatok.nev
            szin = adatok.szin
            self.jatekos_torlese(azonosito)
            self.jatekos_hozzaadasa(azonosito, nev, szin)

    def _szoba_pozicio_biztonsagos(self, sugar, mi = ""):
        for _ in range(600):
            x = self.veletlen.randint(int(sugar * 2), int(self.beallitasok.vilag_szelesseg - sugar * 2))
            y = self.veletlen.randint(int(sugar * 2), int(self.beallitasok.vilag_magassag - sugar * 2))
            if self.jatek_mode == "alma":
                jo = True
                for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, x, y, sugar + self.beallitasok.kigyo_spawn_puffer, 2):
                    if kulcs in self.racs_vilag_kigyo:
                        for _, _, px, py, pr in self.racs_vilag_kigyo[kulcs]:
                            if KorSeged.korok_utkozne_e(x, y, sugar + self.beallitasok.kigyo_spawn_puffer, px, py, pr):
                                jo = False
                                break
                    if not jo:
                        break
                if jo:
                    return float(x), float(y)
            elif self.jatek_mode == "tankos":
                jo = True
                for jatekos in self.jatekosok.values():
                    if KorSeged.korok_utkozne_e(x, y, sugar, jatekos.x, jatekos.y, jatekos.sugar + 30):
                        jo = False
                        break
                if jo:
                    return float(x), float(y)
        return float(self.veletlen.randint(200, self.beallitasok.vilag_szelesseg - 200)), float(self.veletlen.randint(200, self.beallitasok.vilag_magassag - 200))

    def kamera_pozicio(self, azonosito, szelesseg, magassag):
        if azonosito not in self.jatekosok:
            return 0.0, 0.0
        jatekos = self.jatekosok[azonosito]
        if self.jatek_mode == "alma":
            px, py = jatekos.fej_pozicio()
        elif self.jatek_mode == "platformer":
            px, py = jatekos.kamera.apply() #jatekos.kamera.rect.get("x"), jatekos.kamera.rect.get("y")
            #px += jatekos.x
            #py += jatekos.y
        else:
            px, py = jatekos.x, jatekos.y
        return Vector(px - szelesseg / 2, py - magassag / 2)

    def nezet_jatekosnak(self, azonosito, szelesseg, magassag):
        kamera_x, kamera_y = self.kamera_pozicio(azonosito, szelesseg, magassag)
        self.kamera_sugar = szelesseg + magassag
        jatekos = self.jatekosok.get(azonosito)
        #
        # jatekos.kamera.kepernyo_szelesseg = szelesseg
        if self.jatek_mode == "platformer":
            jatekos.kamera.kepernyo_magassag = magassag
            jatekos.kamera.kepernyo_szelesseg = szelesseg

        allapot = {
            "tipus": "nagy",
            "jatek_mode": self.jatek_mode,
            "nehezseg_szint": self.nehezseg_szint,
            "vilag_szelesseg": self.beallitasok.vilag_szelesseg,
            "vilag_magassag": self.beallitasok.vilag_magassag,
            "kamera_x": kamera_x,
            "kamera_y": kamera_y,
            "sajat_id": azonosito,
        }

        if self.jatek_mode == "alma":
            top = sorted(self.osszes_kigyo(), key=lambda k: k.alma_pontok, reverse=True)[:self.beallitasok.top_hany]
            szoveg = []
            for kigyo in top:
                nev = kigyo.nev
                testhossz = len(kigyo.test_pontok)
                oles = kigyo.olesek
                pontszam = kigyo.alma_pontok

                szoveg.append((nev, testhossz, oles, pontszam))
            allapot["toplista"] = szoveg

            allapot["almak"] = self._lathato_almak(kamera_x, kamera_y, szelesseg, magassag)

            allapot["jatekosok"] = {}
            allapot["kigyo_ellenseg"] = []

            sajat = self.jatekosok.get(azonosito)
            if isinstance(sajat, KigyoAdat):
                allapot["jatekosok"][azonosito] = sajat.allapot_dict(
                    kamera_x,
                    kamera_y,
                    szelesseg,
                    magassag,
                    self.beallitasok.kigyo_rajzolas_puffer,
                    self.beallitasok.kigyo_lathato_pont_limit
                )
                allapot["eltelt_ido"] = sajat.eltelt_ido

            lathato_azonositok = self.lathato_kigyo_azonositok(
                kamera_x,
                kamera_y,
                szelesseg,
                magassag,
                sajat_id=azonosito
            )

            ai_lookup = {kigyo.azonosito: kigyo for kigyo in self.kigyo_ellenseg if kigyo.el}

            for masik_azonosito in lathato_azonositok:
                jatekos_kigyo = self.jatekosok.get(masik_azonosito)

                if isinstance(jatekos_kigyo, KigyoAdat) and jatekos_kigyo.el:
                    allapot["jatekosok"][masik_azonosito] = jatekos_kigyo.allapot_dict(
                        kamera_x,
                        kamera_y,
                        szelesseg,
                        magassag,
                        self.beallitasok.kigyo_rajzolas_puffer,
                        self.beallitasok.kigyo_lathato_pont_limit
                    )
                    continue

                ai_kigyo = ai_lookup.get(masik_azonosito)
                if ai_kigyo is not None:
                    allapot["kigyo_ellenseg"].append(
                        ai_kigyo.allapot_dict(
                            kamera_x,
                            kamera_y,
                            szelesseg,
                            magassag,
                            self.beallitasok.kigyo_rajzolas_puffer,
                            self.beallitasok.kigyo_lathato_pont_limit
                        )
                    )
        
        elif self.jatek_mode == "tankos":
            allapot["terkep_resz"] = self.tankos_lathato_terkep_resz(kamera_x, kamera_y, szelesseg, magassag)
            

            allapot["jatekosok"] = {
                az: jatekos.allapot_dict()
                for az, jatekos in self.jatekosok.items()
            }
            allapot["ellensegek_npc"] = {
                az: jatekos.allapot_dict()
                for az, jatekos in self.tank_ellensegek
                }
            allapot["lovedekek"] = self._lathato_lovedekek(kamera_x, kamera_y, szelesseg, magassag)

            allapot["buff"] = self._lathato_chestek(kamera_x, kamera_y, szelesseg, magassag)

        elif self.jatek_mode == "platformer":
            allapot["szoba"] = self.jelenlegi_szoba
            allapot["jatekosok"] = {
                az: jatekos.allapot_dict()
                for az, jatekos in self.jatekosok.items()
            }
        else:
            print(f"ilyen mode nincs: {self.jatek_mode}")

        return allapot

    def nezet_jatekosnak_kicsi(self, azonosito, szelesseg, magassag):
        kamera_x, kamera_y = self.kamera_pozicio(azonosito, szelesseg, magassag)

        allapot = {
            "tipus": "kicsi",
            "jatek_mode": self.jatek_mode,
            "nehezseg_szint": self.nehezseg_szint,
            "vilag_szelesseg": self.beallitasok.vilag_szelesseg,
            "vilag_magassag": self.beallitasok.vilag_magassag,
            "kamera_x": kamera_x,
            "kamera_y": kamera_y,
            "sajat_id": azonosito,
            "almak": [],
            "toplista": [],
            "jatekosok": {},
            "kigyo_ellenseg": [],
        }

        if self.jatek_mode != "alma":
            return self.nezet_jatekosnak(azonosito, szelesseg, magassag)

        sajat = self.jatekosok.get(azonosito)

        if isinstance(sajat, KigyoAdat):
            allapot["jatekosok"][azonosito] = sajat.allapot_dict_kicsi()

        lathato_azonositok = self.lathato_kigyo_azonositok(
            kamera_x,
            kamera_y,
            szelesseg,
            magassag,
            sajat_id=azonosito
        )

        ai_lookup = {kigyo.azonosito: kigyo for kigyo in self.kigyo_ellenseg if kigyo.el}

        for masik_azonosito in lathato_azonositok:
            jatekos_kigyo = self.jatekosok.get(masik_azonosito)

            if isinstance(jatekos_kigyo, KigyoAdat) and jatekos_kigyo.el:
                allapot["jatekosok"][masik_azonosito] = jatekos_kigyo.allapot_dict_kicsi()
                continue

            ai_kigyo = ai_lookup.get(masik_azonosito)
            if ai_kigyo is not None:
                allapot["kigyo_ellenseg"].append(ai_kigyo.allapot_dict_kicsi())

        allapot["almak"] = self._lathato_almak(kamera_x, kamera_y, szelesseg, magassag)
        return allapot

    def mozgas_beallitas(self, azonosito: str, balra: bool, jobbra: bool, fel: bool, le: bool, loves: bool, jump: bool):
        if self.jatek_mode not in ("tankos", "platformer"):
            return

        jatekos = self.jatekosok.get(azonosito)
        try:
            jatekos.mozog_balra = balra
            jatekos.mozog_jobbra = jobbra
            jatekos.mozog_fel = fel
            jatekos.mozog_le = le
            if isinstance(jatekos, Tanki):
                jatekos.loves = loves
            elif isinstance(jatekos, P_elolenyek): # or jatekos.loves
                jatekos.jump = jump
                jatekos.attack = loves
            else: print("nincs ilyen mood  kozos_jatekmag.py -> VilagAllapot -> mozgas_beallitas-ban")
        except:
            pass

    def kep_meret_bealitas(self, azonosito, nev, nev2, x, y):
        eloleny = self.jatekosok.get(azonosito)
        setattr(eloleny, nev, x)
        setattr(eloleny, nev2, y)

    def platformer_spawn_kereses(self, jatekos_szelesseg=40, jatekos_magassag=50):
        if self.platformer_terkep is None:
            return 100, 100

        platform_racs = self.platformer_terkep["platform_racs"]
        racs_meret = self.platformer_terkep["platform_racs_meret"]

        racs_szelesseg = math.ceil(self.platformer_terkep["width"] / racs_meret)
        racs_magassag = math.ceil(self.platformer_terkep["height"] / racs_meret)

        def szilard(cella_x, cella_y):
            platform = platform_racs.get((cella_x, cella_y))

            if platform is None:
                return False

            return platform.get("reteg") == "Collisions"

        # ---------------------------------------------------------
        # 1. Megkeressük a külvilágot.
        #
        # Minden olyan üres cella, amely a térkép széléről elérhető,
        # a játszható barlangon KÍVÜL van.
        # ---------------------------------------------------------

        kulso_terulet = set()
        sor = deque()

        for cella_x in range(racs_szelesseg):
            if not szilard(cella_x, 0):
                kulso_terulet.add((cella_x, 0))
                sor.append((cella_x, 0))

            if not szilard(cella_x, racs_magassag - 1):
                kulso_terulet.add((cella_x, racs_magassag - 1))
                sor.append((cella_x, racs_magassag - 1))

        for cella_y in range(racs_magassag):
            if not szilard(0, cella_y):
                kulso_terulet.add((0, cella_y))
                sor.append((0, cella_y))

            if not szilard(racs_szelesseg - 1, cella_y):
                kulso_terulet.add((racs_szelesseg - 1, cella_y))
                sor.append((racs_szelesseg - 1, cella_y))

        iranyok = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

        while sor:
            cella_x, cella_y = sor.popleft()

            for dx, dy in iranyok:
                uj_x = cella_x + dx
                uj_y = cella_y + dy

                if uj_x < 0 or uj_x >= racs_szelesseg:
                    continue

                if uj_y < 0 or uj_y >= racs_magassag:
                    continue

                if (uj_x, uj_y) in kulso_terulet:
                    continue

                if szilard(uj_x, uj_y):
                    continue

                kulso_terulet.add((uj_x, uj_y))
                sor.append((uj_x, uj_y))

        # ---------------------------------------------------------
        # 2. Megkeressük a legnagyobb zárt belső területet.
        # ---------------------------------------------------------

        mar_megneztuk = set()
        legnagyobb_belso_terulet = set()

        for cella_y in range(racs_magassag):
            for cella_x in range(racs_szelesseg):

                if szilard(cella_x, cella_y):
                    continue

                if (cella_x, cella_y) in kulso_terulet:
                    continue

                if (cella_x, cella_y) in mar_megneztuk:
                    continue

                jelenlegi_terulet = set()
                sor = deque()

                sor.append((cella_x, cella_y))
                mar_megneztuk.add((cella_x, cella_y))

                while sor:
                    x, y = sor.popleft()
                    jelenlegi_terulet.add((x, y))

                    for dx, dy in iranyok:
                        uj_x = x + dx
                        uj_y = y + dy

                        if uj_x < 0 or uj_x >= racs_szelesseg:
                            continue

                        if uj_y < 0 or uj_y >= racs_magassag:
                            continue

                        if szilard(uj_x, uj_y):
                            continue

                        if (uj_x, uj_y) in kulso_terulet:
                            continue

                        if (uj_x, uj_y) in mar_megneztuk:
                            continue

                        mar_megneztuk.add((uj_x, uj_y))
                        sor.append((uj_x, uj_y))

                if len(jelenlegi_terulet) > len(legnagyobb_belso_terulet):
                    legnagyobb_belso_terulet = jelenlegi_terulet

        if not legnagyobb_belso_terulet:
            print("Nincs zárt belső járható terület!")
            return 100, 100

        # ---------------------------------------------------------
        # 3. A karakter mérete cellákban.
        # ---------------------------------------------------------

        jatekos_cella_szelesseg = max(1, math.ceil(jatekos_szelesseg / racs_meret))
        jatekos_cella_magassag = max(1, math.ceil(jatekos_magassag / racs_meret))

        lehetseges_helyek = []

        # ---------------------------------------------------------
        # 4. Csak a BELÜL található rendes padlókat keressük.
        # ---------------------------------------------------------

        for talaj_y in range(jatekos_cella_magassag, racs_magassag):

            for kezdo_x in range(1, racs_szelesseg - jatekos_cella_szelesseg - 1):

                # A játékos alatt legyen összefüggő Collision talaj.
                rendes_talaj = True

                for x in range(kezdo_x - 1, kezdo_x + jatekos_cella_szelesseg + 1):
                    if not szilard(x, talaj_y):
                        rendes_talaj = False
                        break

                if not rendes_talaj:
                    continue

                felso_y = talaj_y - jatekos_cella_magassag

                # A játékos teljes helye a valódi belső járható
                # terület része legyen.
                hely_szabad = True

                for y in range(felso_y, talaj_y):
                    for x in range(kezdo_x, kezdo_x + jatekos_cella_szelesseg):

                        if (x, y) not in legnagyobb_belso_terulet:
                            hely_szabad = False
                            break

                    if not hely_szabad:
                        break

                if not hely_szabad:
                    continue

                x = (kezdo_x * racs_meret + (jatekos_cella_szelesseg * racs_meret - jatekos_szelesseg) / 2)
                y = (talaj_y * racs_meret - jatekos_magassag)

                lehetseges_helyek.append((x, y))

        if not lehetseges_helyek:
            print("A belső területen nem találtam megfelelő spawn helyet!")
            return 100, 100

        # ---------------------------------------------------------
        # 5. A belső játszható terület közepéhez közeli helyet választ.
        # ---------------------------------------------------------

        belso_kozep_x = sum(cella[0] for cella in legnagyobb_belso_terulet) / len(legnagyobb_belso_terulet)
        belso_kozep_y = sum(cella[1] for cella in legnagyobb_belso_terulet) / len(legnagyobb_belso_terulet)

        legjobb_hely = min(
            lehetseges_helyek,
            key=lambda hely: (hely[0] / racs_meret - belso_kozep_x) ** 2 + (hely[1] / racs_meret - belso_kozep_y) ** 2
        )

        print("Platformer spawn:", legjobb_hely)

        return legjobb_hely
        # --------------- CSAK KÍGYÓS MÓD ------------------




    # -------------kigyo -----------------------
    def kigyo_celszam(self, nehezseg_szint):
        if nehezseg_szint == "Easy":
            return 120
        if nehezseg_szint == "Normal":
            return 180
        if nehezseg_szint == "Hard":
            return 220
        if nehezseg_szint == "Nightmare":
            return 250
        if nehezseg_szint == "Hell":
            return 280
        return 180

    def _kezdo_alma_db(self):
        if self.nehezseg_szint == "Easy":
            return 2000
        if self.nehezseg_szint == "Normal":
            return 3000
        if self.nehezseg_szint == "Hard":
            return 4000
        if self.nehezseg_szint == "Nightmare":
            return 5000
        return 6000

    def jatekos_irany_beallitasa(self, azonosito, dx, dy) :
        if self.jatek_mode != "alma":
            return
        kigyo = self.jatekosok.get(azonosito)
        if isinstance(kigyo, KigyoAdat):
            kigyo.beallit_irany(dx, dy)

    def jatekos_gyorsitas_beallitasa(self, azonosito, gyors) :
        if self.jatek_mode != "alma":
            return
        kigyo = self.jatekosok.get(azonosito)
        if isinstance(kigyo, KigyoAdat) :
            if gyors and len(kigyo.test_pontok) >= self.beallitasok.kigyo_alap_hossz + 1:
                kigyo.gyorsit = gyors
                kigyo.cel_sebesseg = kigyo.alap_sebesseg * 2.0 if gyors else kigyo.alap_sebesseg
                kigyo.vesztes_testhosz_szamulo += 1
                if kigyo.vesztes_testhosz_szamulo % self.beallitasok.kigyo_csokenes_sebeseg == 0:
                    self.racs_vilag_alma[kigyo.utolso_racs[-1]].append(kigyo.test_pontok[-1])
                    kigyo.hosz_vesztes()
            else:
                kigyo.cel_sebesseg = kigyo.alap_sebesseg

    def _alma_mod_frissites(self, delta_ido) :
        if not self.jatekosok and not self.kigyo_ellenseg:
            return
        
        for kigyo in self.osszes_kigyo():
            if not kigyo.el:
                continue
            kigyo.eltelt_ido += delta_ido
            if kigyo.jatekos_e:
                kigyo.sebesseg += (kigyo.cel_sebesseg - kigyo.sebesseg) * 0.18
            else:
                cel_dx, cel_dy = self._legjobb_irany_ai(kigyo, delta_ido)
                uj_dx, uj_dy = self._forditas_korlatozva(kigyo.irany_x, kigyo.irany_y, cel_dx, cel_dy)
                kigyo.irany_x, kigyo.irany_y = KorSeged.normalizal(uj_dx, uj_dy)
                kigyo.sebesseg = kigyo.alap_sebesseg
            self._kigyo_fej_leptetes(kigyo, delta_ido)
        self._kigyok_racsozasa()
        for kigyo in self.osszes_kigyo():
            if not kigyo.el:
                continue
            self._kigyo_etetes(kigyo)
            self._kigyo_utkozesek(kigyo)

        halott_ai_kigyok = [k for k in self.kigyo_ellenseg if not k.el]
        self.kigyo_to_almak(halott_ai_kigyok)
        for kigyo in halott_ai_kigyok:
            self._kigyo_racsbol_torles(kigyo)

        self.kigyo_ellenseg = [k for k in self.kigyo_ellenseg if k.el]
        
        self.alma_potlasi_idozito += 1
        if self.alma_potlasi_idozito >= 10:
            self.alma_potlasi_idozito = 0
            hianyzik = self._kezdo_alma_db() - self.almak_szama()
            if hianyzik > 0:
                self._almak_generalasa(min(hianyzik, self.beallitasok.alma_potlasi_limit))

        self.kigyo_respawn_idozito += 1
        if self.kigyo_respawn_idozito >= self.beallitasok.kigyo_respawn_varakozas:
            self.kigyo_respawn_idozito = 0
            hiany = self.max_kigyok - len(self.kigyo_ellenseg)
            if hiany > 0:
                self._ai_kigyok_potlas(min(hiany, 2))

        halott_jatekos_azonositok = []

        for azonosito, jatekos in self.jatekosok.items():
            if isinstance(jatekos, KigyoAdat) and not jatekos.el:
                halott_jatekos_azonositok.append(azonosito)

        for azonosito in halott_jatekos_azonositok:
            self.jatekos_torlese(azonosito)
        self.frissitesi_szamlalo += 1

    def _almak_generalasa(self, mennyiseg) :
        jelenlegi = self.almak_szama()
        cel = min(self.beallitasok.alma_maximum, jelenlegi + mennyiseg)
        while self.almak_szama() < cel:
            x = self.veletlen.randint(50, self.beallitasok.vilag_szelesseg - 50)
            y = self.veletlen.randint(50, self.beallitasok.vilag_magassag - 50)
            kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, x, y)
            if not self._alma_tul_kozel(x, y):
                self.racs_vilag_alma[kulcs].append((float(x), float(y)))

    def _alma_tul_kozel(self, x, y):
        sugar = self.beallitasok.alma_size * 1.4
        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, x, y, sugar, 1):
            for ax, ay in self.racs_vilag_alma.get(kulcs, []):
                if KorSeged.korok_utkozne_e(x, y, self.beallitasok.alma_kor_sugár, ax, ay, self.beallitasok.alma_kor_sugár):
                    return True
        return False

    def almak_szama(self):
        return sum(len(ertek) for ertek in self.racs_vilag_alma.values())

    def _ai_kigyok_potlas(self, mennyiseg) :
        for _ in range(mennyiseg):
            self.eddigi_kigyok += 1
            nev = f"AI_{self.eddigi_kigyok}"
            szin = SzinSeged.veletlen_szin()
            x, y = self._szoba_pozicio_biztonsagos(self.beallitasok.kigyó_sugár, "kigyo")
            uj = KigyoAdat(nev, nev, szin, self.nehezseg_szint, x, y, self.beallitasok, False)
            uj.irany_x, uj.irany_y = KorSeged.normalizal(self.veletlen.uniform(-1.0, 1.0), self.veletlen.uniform(-1.0, 1.0))
            uj.dontes_fazis = self.dontes_kiosztas
            self.dontes_kiosztas += 1
            if self.dontes_kiosztas >= uj.dontes_gyakorisag:
                self.dontes_kiosztas = 0
            self.kigyo_ellenseg.append(uj)
            self.racs_kigyo_hozzaad(uj)

    def osszes_kigyo(self):
        eredmeny = []
        for j in self.jatekosok.values():
            if isinstance(j, KigyoAdat):
                eredmeny.append(j)
        eredmeny.extend(self.kigyo_ellenseg)
        return eredmeny

    def _kigyo_racs_rekord_index(self, cella_lista, azonosito, index):
        for poz, rekord in enumerate(cella_lista):
            rekord_azonosito, rekord_index, _, _, _ = rekord
            if rekord_azonosito == azonosito and rekord_index == index:
                return poz
        return -1

    def _kigyo_racsbol_torles(self, kigyo: KigyoAdat) :
        if not hasattr(kigyo, "utolso_racs"):
            return

        for index, regi_kulcs in enumerate(kigyo.utolso_racs):
            if regi_kulcs is None:
                continue

            cella_lista = self.racs_vilag_kigyo.get(regi_kulcs)
            if not cella_lista:
                continue

            regi_poz = self._kigyo_racs_rekord_index(cella_lista, kigyo.azonosito, index)
            if regi_poz != -1:
                del cella_lista[regi_poz]
                if not cella_lista:
                    del self.racs_vilag_kigyo[regi_kulcs]

        kigyo.utolso_racs = [None] * len(kigyo.test_pontok)

    def _kigyok_racsozasa(self) :
        for kigyo in self.osszes_kigyo():
            if not kigyo.el:
                continue

            pont_db = len(kigyo.test_pontok)

            if not hasattr(kigyo, "utolso_racs"):
                kigyo.utolso_racs = [None] * pont_db

            if len(kigyo.utolso_racs) < pont_db:
                kigyo.utolso_racs.extend([None] * (pont_db - len(kigyo.utolso_racs)))

            elif len(kigyo.utolso_racs) > pont_db:
                for index in range(pont_db, len(kigyo.utolso_racs)):
                    regi_kulcs = kigyo.utolso_racs[index]
                    if regi_kulcs is not None:
                        cella_lista = self.racs_vilag_kigyo.get(regi_kulcs)
                        if cella_lista:
                            regi_poz = self._kigyo_racs_rekord_index(cella_lista, kigyo.azonosito, index)
                            if regi_poz != -1:
                                del cella_lista[regi_poz]
                                if not cella_lista:
                                    del self.racs_vilag_kigyo[regi_kulcs]
                del kigyo.utolso_racs[pont_db:]

            for index, (x, y) in enumerate(kigyo.test_pontok):
                uj_kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, x, y)
                regi_kulcs = kigyo.utolso_racs[index]

                if regi_kulcs is None:
                    self.racs_vilag_kigyo[uj_kulcs].append((kigyo.azonosito, index, x, y, kigyo.sugar))
                    kigyo.utolso_racs[index] = uj_kulcs
                    continue

                if regi_kulcs == uj_kulcs:
                    cella_lista = self.racs_vilag_kigyo.get(uj_kulcs)
                    if cella_lista is None:
                        self.racs_vilag_kigyo[uj_kulcs] = [(kigyo.azonosito, index, x, y, kigyo.sugar)]
                        continue

                    regi_poz = self._kigyo_racs_rekord_index(cella_lista, kigyo.azonosito, index)
                    if regi_poz != -1:
                        cella_lista[regi_poz] = (kigyo.azonosito, index, x, y, kigyo.sugar)
                    else:
                        cella_lista.append((kigyo.azonosito, index, x, y, kigyo.sugar))
                    continue

                regi_lista = self.racs_vilag_kigyo.get(regi_kulcs)
                if regi_lista:
                    regi_poz = self._kigyo_racs_rekord_index(regi_lista, kigyo.azonosito, index)
                    if regi_poz != -1:
                        del regi_lista[regi_poz]
                        if not regi_lista:
                            del self.racs_vilag_kigyo[regi_kulcs]

                self.racs_vilag_kigyo[uj_kulcs].append((kigyo.azonosito, index, x, y, kigyo.sugar))
                kigyo.utolso_racs[index] = uj_kulcs           

    def racs_kigyo_hozzaad(self, kigyo: KigyoAdat):
        kigyo.utolso_racs = []
        for index, (x, y) in enumerate(kigyo.test_pontok):
            kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, x, y)
            self.racs_vilag_kigyo[kulcs].append((kigyo.azonosito, index, x, y, kigyo.sugar))
            kigyo.utolso_racs.append(kulcs)

    def kigyo_to_almak(self, kigyok):
        for kigyo in kigyok:
            for x, y in kigyo.test_pontok:
                db = self.veletlen.randint(1, 2)

                for _ in range(db):
                    uj_x = x + self.veletlen.uniform(-22, 22)
                    uj_y = y + self.veletlen.uniform(-22, 22)

                    uj_x = max(20, min(self.beallitasok.vilag_szelesseg - 20, uj_x))
                    uj_y = max(20, min(self.beallitasok.vilag_magassag - 20, uj_y))

                    if not self._alma_tul_kozel(uj_x, uj_y):
                        kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, uj_x, uj_y)
                        self.racs_vilag_alma[kulcs].append((uj_x, uj_y))

    def _kigyo_fej_leptetes(self, kigyo: KigyoAdat, delta_ido) :
        fej_x, fej_y = kigyo.test_pontok[0]
        kigyo.test_pontok[0][0] = fej_x + kigyo.irany_x * kigyo.sebesseg * delta_ido
        kigyo.test_pontok[0][1] = fej_y + kigyo.irany_y * kigyo.sebesseg * delta_ido
        kigyo.utvonal.insert(0, list(kigyo.test_pontok[0]))

        utvonal_index = 0
        for index in range(1, len(kigyo.test_pontok)):
            elozo_x, elozo_y = kigyo.test_pontok[index - 1]
            talalt = False
            while utvonal_index < len(kigyo.utvonal):
                pont_x, pont_y = kigyo.utvonal[utvonal_index]
                tav = KorSeged.tavolsag(elozo_x, elozo_y, pont_x, pont_y)
                if tav >= kigyo.idealis_tavolsag:
                    arany = kigyo.idealis_tavolsag / max(tav, 1e-6)
                    uj_x = elozo_x + (pont_x - elozo_x) * arany
                    uj_y = elozo_y + (pont_y - elozo_y) * arany
                    kigyo.test_pontok[index] = [uj_x, uj_y]
                    talalt = True
                    break
                utvonal_index += 1
            if not talalt and kigyo.utvonal:
                kigyo.test_pontok[index] = list(kigyo.utvonal[-1])

        max_pont = max(40, len(kigyo.test_pontok) * self.beallitasok.kigyo_max_memoria_szorzo)
        if len(kigyo.utvonal) > max_pont:
            kigyo.utvonal = kigyo.utvonal[:max_pont]

    def _kigyo_etetes(self, kigyo: KigyoAdat) :
        fej_x, fej_y = kigyo.fej_pozicio()
        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, fej_x, fej_y, kigyo.sugar + self.beallitasok.alma_kor_sugár, 1):
            almak = self.racs_vilag_alma.get(kulcs)
            if not almak:
                continue
            for index in range(len(almak) - 1, -1, -1):
                alma_x, alma_y = almak[index]
                if KorSeged.korok_utkozne_e(fej_x, fej_y, kigyo.sugar, alma_x, alma_y, self.beallitasok.alma_kor_sugár):
                    del almak[index]
                    if not almak:
                        del self.racs_vilag_alma[kulcs]
                    kigyo.novekedes(self.beallitasok)
                    kigyo.alma_pontok += 1
                    break

    def _kigyo_utkozesek(self, kigyo: KigyoAdat) :
        fej_x, fej_y = kigyo.fej_pozicio()
        sugar = kigyo.sugar

        if fej_x - sugar < 0 or fej_x + sugar > self.beallitasok.vilag_szelesseg or fej_y - sugar < 0 or fej_y + sugar > self.beallitasok.vilag_magassag:
            kigyo.el = False
            return

        marvizsgalt = set()
        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, fej_x, fej_y, sugar * 2.5, 1):
            for idegen_id, pont_index, px, py, psugar in self.racs_vilag_kigyo.get(kulcs, []):
                kulcs2 = (idegen_id, pont_index)
                if kulcs2 in marvizsgalt:
                    continue
                marvizsgalt.add(kulcs2)
                if idegen_id == kigyo.azonosito:
                    continue
                if KorSeged.korok_utkozne_e(fej_x, fej_y, sugar, px, py, psugar * self.beallitasok.kigyo_utkozes_szorzo / 2):
                    kigyo.el = False
                    if idegen_id != kigyo.azonosito:
                        gyilkos = self._kigyo_keresese(idegen_id)
                        if gyilkos is not None:
                            gyilkos.olesek += 1
                    return

    def _kigyo_keresese(self, azonosito):
        for kigyo in self.osszes_kigyo():
            if kigyo.azonosito == azonosito:
                return kigyo
        return None

    def _kozelebbi_almak(self, x: float, y: float):
        eredmeny = []
        keresesi_tav = self.beallitasok.racsok_nagysaga * 2.2

        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, x, y, keresesi_tav, 2):
            eredmeny.extend(self.racs_vilag_alma.get(kulcs, []))

        if not eredmeny:
            return []

        eredmeny.sort(key=lambda alma: KorSeged.tavolsag(x, y, alma[0], alma[1]))
        return eredmeny[:40]

    def _legjobb_irany_ai(self, kigyo: KigyoAdat, delta_ido):
        if self.frissitesi_szamlalo % kigyo.dontes_gyakorisag != kigyo.dontes_fazis:
            return kigyo.irany_x, kigyo.irany_y

        fej_x, fej_y = kigyo.fej_pozicio()

        almak = self._kozelebbi_almak(fej_x, fej_y)
        cel_x, cel_y = self._celpont_kereses(kigyo, almak)

        alma_dx = cel_x - fej_x
        alma_dy = cel_y - fej_y
        alap_dx, alap_dy = KorSeged.normalizal(alma_dx, alma_dy)

        if abs(alap_dx) < 1e-6 and abs(alap_dy) < 1e-6:
            alap_dx, alap_dy = kigyo.irany_x, kigyo.irany_y

        veszely_tav = 50.0 + kigyo.sugar
        fal_puffer = kigyo.sugar + 10.0

        bal_tav = fej_x
        jobb_tav = self.beallitasok.vilag_szelesseg - fej_x
        fent_tav = fej_y
        lent_tav = self.beallitasok.vilag_magassag - fej_y

        menekulo_x = 0.0
        menekulo_y = 0.0
        veszely_van = False

        if bal_tav < veszely_tav:
            menekulo_x += 1.0
            veszely_van = True
        if jobb_tav < veszely_tav:
            menekulo_x -= 1.0
            veszely_van = True
        if fent_tav < veszely_tav:
            menekulo_y += 1.0
            veszely_van = True
        if lent_tav < veszely_tav:
            menekulo_y -= 1.0
            veszely_van = True

        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, fej_x, fej_y,veszely_tav, 1):
            for idegen_id, pont_index, px, py, psugar in self.racs_vilag_kigyo.get(kulcs, []):
                if idegen_id == kigyo.azonosito:
                    continue

                tav = KorSeged.tavolsag(fej_x, fej_y, px, py)
                hatar = veszely_tav + psugar

                if tav < hatar and tav > 1e-6:
                    veszely_van = True
                    menekulo_x += (fej_x - px) / tav
                    menekulo_y += (fej_y - py) / tav

        if veszely_van:
            dx, dy = KorSeged.normalizal(menekulo_x, menekulo_y)

            if abs(dx) > 1e-6 or abs(dy) > 1e-6:
                return dx, dy

            balra_dx, balra_dy = -kigyo.irany_y, kigyo.irany_x
            jobbra_dx, jobbra_dy = kigyo.irany_y, -kigyo.irany_x

            balra_bizt = self._irany_biztonsagos(kigyo, balra_dx, balra_dy, veszely_tav)
            jobbra_bizt = self._irany_biztonsagos(kigyo, jobbra_dx, jobbra_dy, veszely_tav)

            if balra_bizt and not jobbra_bizt:
                return KorSeged.normalizal(balra_dx, balra_dy)
            if jobbra_bizt and not balra_bizt:
                return KorSeged.normalizal(jobbra_dx, jobbra_dy)

            return KorSeged.normalizal(balra_dx, balra_dy)

        if self._irany_biztonsagos(kigyo, alap_dx, alap_dy, 38.0):
            return alap_dx, alap_dy

        
        legjobb_dx, legjobb_dy = kigyo.irany_x, kigyo.irany_y
        legjobb_tav = float("inf")

        aktualis_szog = math.atan2(alap_dy, alap_dx)
        for fok in (-90, -60, -30, 30, 60, 90, 120, -120, 180):
            szog = aktualis_szog + math.radians(fok)
            dx = math.cos(szog)
            dy = math.sin(szog)

            if not self._irany_biztonsagos(kigyo, dx, dy, 38.0):
                continue

            becsult_x = fej_x + dx * 220.0
            becsult_y = fej_y + dy * 220.0
            tav = KorSeged.tavolsag(becsult_x, becsult_y, cel_x, cel_y)

            if tav < legjobb_tav:
                legjobb_tav = tav
                legjobb_dx = dx
                legjobb_dy = dy

        return KorSeged.normalizal(legjobb_dx, legjobb_dy)

    def _celpont_kereses(self, kigyo: KigyoAdat, almak):
        fej_x, fej_y = kigyo.fej_pozicio()

        if almak:
            legjobb = None
            legjobb_tav = float("inf")

            for alma_x, alma_y in almak:
                tav = KorSeged.tavolsag(fej_x, fej_y, alma_x, alma_y)
                if self.kordinata_kozti_kordinata((fej_x, fej_y), (alma_x, alma_y)):
                    if tav < legjobb_tav:
                        legjobb_tav = tav
                        legjobb = (alma_x, alma_y)

            if legjobb is not None:
                return legjobb

        return (fej_x + kigyo.irany_x * 180.0, fej_y + kigyo.irany_y * 180.0)

    def kordinata_kozti_kordinata(self, indulas, erkezes):
        """True = nincs akadály közte, False = van akadály közte."""

        x, y = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, indulas[0], indulas[1])
        x1, y1 = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, erkezes[0], erkezes[1])

        dx = abs(x1 - x)
        dy = abs(y1 - y)

        sx = 1 if x < x1 else -1
        sy = 1 if y < y1 else -1

        err = dx - dy
        elso = True

        while True:
            if not elso:
                if self.racs_vilag_kigyo.get((x, y), 0):
                    return False

            elso = False

            if (x, y) == (x1, y1):
                return True

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x += sx

            if e2 < dx:
                err += dx
                y += sy

    def _irany_biztonsagos(self, kigyo: KigyoAdat, dx, dy, veszely_tav):
        fej_x, fej_y = kigyo.fej_pozicio()

        for minta in (0.35, 0.7, 1.0):
            px = fej_x + dx * veszely_tav * minta
            py = fej_y + dy * veszely_tav * minta

            if (px < kigyo.sugar or px > self.beallitasok.vilag_szelesseg - kigyo.sugar or py < kigyo.sugar or py > self.beallitasok.vilag_magassag - kigyo.sugar):
                return False

            for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, px, py, kigyo.sugar * 2.5, 1):
                for idegen_id, pont_index, resz_x, resz_y, resz_sugar in self.racs_vilag_kigyo.get(kulcs, []):
                    if idegen_id == kigyo.azonosito:
                        continue

                    if KorSeged.korok_utkozne_e(px, py, kigyo.sugar, resz_x, resz_y, resz_sugar):
                        return False

        return True

    def _minta_veszely_pont(self, kigyo: KigyoAdat, px, py):
        buntetes = 0.0
        mintakulcsok = KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, px, py, kigyo.sugar * 3, 1)
        for kulcs in mintakulcsok:
            for idegen_id, pont_index, resz_x, resz_y, resz_sugar in self.racs_vilag_kigyo.get(kulcs, []):
                if idegen_id == kigyo.azonosito:
                    continue
                tav = KorSeged.tavolsag(px, py, resz_x, resz_y)
                if tav < kigyo.sugar * 3.0:
                    buntetes += max(0.0, 5000.0 - tav * 150.0)
        return buntetes

    def lathato_kigyo_azonositok(self, kamera_x, kamera_y, szelesseg, magassag, sajat_id = None):
        bal = kamera_x - self.beallitasok.kigyo_rajzolas_puffer
        jobb = kamera_x + szelesseg + self.beallitasok.kigyo_rajzolas_puffer
        fent = kamera_y - self.beallitasok.kigyo_rajzolas_puffer
        lent = kamera_y + magassag + self.beallitasok.kigyo_rajzolas_puffer

        start_cx, start_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, bal, fent)
        end_cx, end_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jobb, lent)

        eredmeny = set()

        for cx in range(start_cx - 1, end_cx + 2):
            for cy in range(start_cy - 1, end_cy + 2):
                for azonosito, index, x, y, sugar in self.racs_vilag_kigyo.get((cx, cy), []):
                    if sajat_id is not None and azonosito == sajat_id:
                        continue

                    if bal < x < jobb and fent < y < lent:
                        eredmeny.add(azonosito)

        return eredmeny

    def kicsi_csomag_mozgatas(self, info, regi, szelesseg, magassag):
        """A kicsi csomagot útvonal alapján mozgatja rá az előző nagy csomagra."""

        if not regi:
            return info

        regi["kamera_x"] = info.get("kamera_x", regi.get("kamera_x", 0.0))
        regi["kamera_y"] = info.get("kamera_y", regi.get("kamera_y", 0.0))
        regi["almak"] = info.get("almak", regi.get("almak", []))

        def pont_utvonalrol(utvonal, keresett_tav):
            if not utvonal:
                return [0.0, 0.0]

            if len(utvonal) == 1:
                return list(utvonal[0])

            maradek = keresett_tav

            for index in range(len(utvonal) - 1):
                x1, y1 = utvonal[index]
                x2, y2 = utvonal[index + 1]

                szakasz = KorSeged.tavolsag(x1, y1, x2, y2)

                if szakasz >= maradek:
                    arany = maradek / max(szakasz, 1e-6)
                    return [
                        x1 + (x2 - x1) * arany,
                        y1 + (y2 - y1) * arany
                    ]

                maradek -= szakasz

            return list(utvonal[-1])

        def utvonal_vagas(utvonal, max_tav):
            if len(utvonal) <= 2:
                return utvonal

            uj_utvonal = [utvonal[0]]
            eddigi_tav = 0.0

            for index in range(len(utvonal) - 1):
                x1, y1 = utvonal[index]
                x2, y2 = utvonal[index + 1]
                szakasz = KorSeged.tavolsag(x1, y1, x2, y2)

                if eddigi_tav + szakasz > max_tav:
                    maradek = max_tav - eddigi_tav
                    arany = maradek / max(szakasz, 1e-6)
                    uj_utvonal.append([
                        x1 + (x2 - x1) * arany,
                        y1 + (y2 - y1) * arany
                    ])
                    break

                uj_utvonal.append([x2, y2])
                eddigi_tav += szakasz

            return uj_utvonal

        def kigyo_mozgatas(regi_kigyo, kicsi_kigyo):
            if not regi_kigyo or not kicsi_kigyo:
                return

            if not kicsi_kigyo.get("el", True):
                regi_kigyo["el"] = False
                return

            test_pontok = regi_kigyo.get("test_pontok", [])
            if not test_pontok:
                return

            uj_fej_x = kicsi_kigyo.get("fej_x", test_pontok[0][0])
            uj_fej_y = kicsi_kigyo.get("fej_y", test_pontok[0][1])

            cel_hossz = kicsi_kigyo.get("ossz_testhosz", len(test_pontok))
            idealis_tav = self.beallitasok.kigyo_resz_tav

            utvonal = regi_kigyo.get("utvonal")
            if not utvonal:
                utvonal = [pont[:] for pont in test_pontok]

            regi_fej_x, regi_fej_y = utvonal[0]
            if KorSeged.tavolsag(regi_fej_x, regi_fej_y, uj_fej_x, uj_fej_y) > 0.1:
                utvonal.insert(0, [uj_fej_x, uj_fej_y])
            else:
                utvonal[0] = [uj_fej_x, uj_fej_y]

            max_utvonal_tav = max(120.0, cel_hossz * idealis_tav * 2.5)
            utvonal = utvonal_vagas(utvonal, max_utvonal_tav)

            uj_test_pontok = []
            for index in range(cel_hossz):
                keresett_tav = index * idealis_tav
                uj_test_pontok.append(pont_utvonalrol(utvonal, keresett_tav))

            regi_kigyo["test_pontok"] = uj_test_pontok
            regi_kigyo["utvonal"] = utvonal
            regi_kigyo["el"] = True
            regi_kigyo["ossz_testhosz"] = cel_hossz

        for azonosito, kicsi_kigyo in info.get("jatekosok", {}).items():
            regi_kigyo = regi.get("jatekosok", {}).get(azonosito)
            kigyo_mozgatas(regi_kigyo, kicsi_kigyo)

        regi_ai_lookup = {
            kigyo.get("azonosito"): kigyo
            for kigyo in regi.get("kigyo_ellenseg", [])
        }

        for kicsi_kigyo in info.get("kigyo_ellenseg", []):
            azonosito = kicsi_kigyo.get("azonosito")
            regi_kigyo = regi_ai_lookup.get(azonosito)
            kigyo_mozgatas(regi_kigyo, kicsi_kigyo)
        
        return regi

    def _lathato_almak(self, kamera_x, kamera_y, szelesseg, magassag):
        bal = kamera_x - self.beallitasok.alma_rajzolas_puffer
        jobb = kamera_x + szelesseg + self.beallitasok.alma_rajzolas_puffer
        fent = kamera_y - self.beallitasok.alma_rajzolas_puffer
        lent = kamera_y + magassag + self.beallitasok.alma_rajzolas_puffer
        start_cx, start_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, bal, fent)
        end_cx, end_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jobb, lent)
        eredmeny = []
        for cx in range(start_cx - 1, end_cx + 2):
            for cy in range(start_cy - 1, end_cy + 2):
                for alma_x, alma_y in self.racs_vilag_alma.get((cx, cy), []):
                    if bal < alma_x < jobb and fent < alma_y < lent:
                        eredmeny.append((alma_x, alma_y))
                        if len(eredmeny) >= self.beallitasok.alma_lathato_limit:
                            return eredmeny
        return eredmeny

    def _forditas_korlatozva(self, aktualis_dx, aktualis_dy, cel_dx, cel_dy):
        aktualis_szog = math.atan2(aktualis_dy, aktualis_dx)
        cel_szog = math.atan2(cel_dy, cel_dx)

        delta_szog = cel_szog - aktualis_szog

        while delta_szog > math.pi:
            delta_szog -= 2 * math.pi
        while delta_szog < -math.pi:
            delta_szog += 2 * math.pi

        max_fordulas = math.radians(self.beallitasok.kigyo_max_fordulas_fok)

        if delta_szog > max_fordulas:
            uj_szog = aktualis_szog + max_fordulas
        elif delta_szog < -max_fordulas:
            uj_szog = aktualis_szog - max_fordulas
        else:
            uj_szog = cel_szog

        return math.cos(uj_szog), math.sin(uj_szog)


    # ----------------------------- CSAK TANKOS MÓD -----------------------------

    def tankos_kezdes(self, kep= None):
        self.terkep_tank = Tank_Terkep(self, self.tank_szeleseg, self.tank_magassag, cella=90)
        
        self.chestek = [chest for halmaz in self.terkep_tank.chest_racs.values() for chest in halmaz]
        for chest in self.chestek:
            self.tank_chest_racsba_rakas(chest)

        self.beallitasok.vilag_szelesseg = self.terkep_tank.SZEL * self.terkep_tank.CELLA
        self.beallitasok.vilag_magassag = self.terkep_tank.MAG * self.terkep_tank.CELLA
        
        for _ in range(self.ai_db):
            x, y = self._tankos_spawn_pozicio()
            nev = random.choice(NEVEK)
            azonosito = self.eddigi_tankok_npc
            uj = Tanki(azonosito, nev, SzinSeged.veletlen_szin(), x, y, self.beallitasok)
            if kep is not None:
                uj.tank_kep_nev = kep
                self.tank
            #self.tank_ellensegek.append(uj)
            uj.dontes_fazis = self.dontes_kiosztas
            self.dontes_kiosztas += 1
            if self.dontes_kiosztas >= uj.dontes_gyakorisag:
                self.dontes_kiosztas = 0
            self.jatekosok[azonosito] = uj
            self.tank_jatekos_racs_hozzaad(uj)
            self.eddigi_tankok_npc += 1

    def _tankos_spawn_pozicio(self):
        if self.terkep_tank is None:
            return 200.0, 200.0

        cella = self.terkep_tank.CELLA
        sugar = self.beallitasok.jatekos_sugar

        for _ in range(2000):
            sor = self.veletlen.randint(1, self.terkep_tank.MAG - 2)
            oszlop = self.veletlen.randint(1, self.terkep_tank.SZEL - 2)

            x = oszlop * cella + cella / 2
            y = sor * cella + cella / 2

            if not self.terkep_tank.jarhato(sor, oszlop):
                continue

            if not self._tankos_pozicio_jarhato(x, y, sugar):
                continue

            jo = True
            for masik in self.jatekosok.values():
                if KorSeged.korok_utkozne_e(x, y, sugar, masik.x, masik.y, masik.sugar + 30):
                    jo = False
                    break

            if jo:
                return float(x), float(y)

        return 2 * cella + cella / 2, 2 * cella + cella / 2

    def _tankos_pozicio_jarhato(self, x: float, y: float, sugar: float):
        if self.terkep_tank is None:
            return True

        cella = self.terkep_tank.CELLA

        pontok = [
            (x, y),
            (x - sugar, y),
            (x + sugar, y),
            (x, y - sugar),
            (x, y + sugar),
        ]

        for px, py in pontok:
            oszlop = int(px // cella)
            sor = int(py // cella)

            if not self.terkep_tank.jarhato(sor, oszlop):
                return False

        return True

    
    # mozgas
    def _mozgas_tankos_jatekosok(self, delta_ido) :
        for jatekos in self.jatekosok.values():
            if not isinstance(jatekos, Tanki):
                continue

            if not jatekos.el:
                continue

            fordulasi_sebesseg = getattr(jatekos, "fordulasi_sebesseg", 180.0)

            if jatekos.mozog_balra:
                jatekos.fok -= fordulasi_sebesseg * delta_ido

            if jatekos.mozog_jobbra:
                jatekos.fok += fordulasi_sebesseg * delta_ido

            

            jatekos.fok = jatekos.fok % 360

            elore_hatra = 0

            if jatekos.mozog_fel:
                elore_hatra += 1

            if jatekos.mozog_le:
                elore_hatra -= 1

            if elore_hatra == 0:
                continue

            radian = math.radians(jatekos.fok - 90)

            irany_x = math.cos(radian)
            irany_y = math.sin(radian)

            uj_x = jatekos.x + irany_x * jatekos.sebesseg * delta_ido * elore_hatra
            uj_y = jatekos.y + irany_y * jatekos.sebesseg * delta_ido * elore_hatra

            uj_x = max(jatekos.sugar, min(self.beallitasok.vilag_szelesseg - jatekos.sugar, uj_x))
            uj_y = max(jatekos.sugar, min(self.beallitasok.vilag_magassag - jatekos.sugar, uj_y))

            if self._tankos_pozicio_jarhato(uj_x, uj_y, jatekos.sugar) and self._tank_pozicio_szabad(jatekos, uj_x, uj_y):
                jatekos.x = uj_x
                jatekos.y = uj_y
                for i in range(-2, 3):
                    for j in range(-2, 3):
                        jatekos_hely = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jatekos.x, jatekos.y)
                        hely = jatekos_hely[0] - i, jatekos_hely[1] - j
                        for chest in self.racs_vilag_chestdrop[hely[0], hely[1]]:
                            if KorSeged.korok_utkozne_e(chest.x, chest.y, chest.sugar, jatekos.x, jatekos.y, jatekos.sugar):
                                chest.kincs_lathato = False
                                definicio = getattr(Buffok, chest.buff[:-1] if chest.buff is not "teleport" else chest.buff)
                                self.tank_chestdrop_racsbol_torles(chest)
                                jatekos.buff_hozzaadasa(chest.buff, definicio, chest.ertek, chest.ido)
                                break
                self.tank_jatekos_racs_frissit(jatekos)

    def _tankos_mod_frissites(self, delta_ido) :
        if not self.jatekosok:
            return

        for jatekos in self.jatekosok.values():
            if isinstance(jatekos, Tanki) and jatekos.el:
 
                jatekos.eltelt_ido += delta_ido
                if jatekos.tuzeles(delta_ido):
                    radian = math.radians(jatekos.fok - 90)
                    
                    irany_x = math.cos(radian)
                    irany_y = math.sin(radian)
                    lovedek_x = jatekos.x + irany_x * jatekos.sugar
                    lovedek_y = jatekos.y + irany_y * jatekos.sugar
                    racs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, lovedek_x, lovedek_y)
                    lovedek = Lovedek(self.lovedek_azonosito, jatekos.azonosito, lovedek_x, lovedek_y, irany_x, irany_y)
                    lovedek.utolso_racs = racs
                    jatekos.tuzelt = True
                    self.lovedekek.append(lovedek)
                    self.racs_vilag_lovedekek[racs].add(lovedek)
                    
                    self.lovedek_azonosito += 1
                    
            jatekos.buff_kezelo(delta_ido)
        self.tank_npc_mozgatas_loves(delta_ido)
        self.lovedek_racs_frisitese_mozgatasa(delta_ido)
        self._mozgas_tankos_jatekosok(delta_ido)
        self.chest_potlas()

    def tank_jatekos_racs_hozzaad(self, jatekos):
        kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jatekos.x, jatekos.y)
        self.racs_vilag_tank_jatekosok[kulcs].add(jatekos.azonosito)
        jatekos.utolso_racs = kulcs

    def tank_jatekos_racsbol_torles(self, jatekos):
        if getattr(jatekos, "utolso_racs", None) is None:
            return

        regi_kulcs = jatekos.utolso_racs

        if regi_kulcs in self.racs_vilag_tank_jatekosok:
            self.racs_vilag_tank_jatekosok[regi_kulcs].discard(jatekos.azonosito)

            if not self.racs_vilag_tank_jatekosok[regi_kulcs]:
                del self.racs_vilag_tank_jatekosok[regi_kulcs]

        jatekos.utolso_racs = None

    def tank_chest_racsbol_torles(self, chest):
        hely = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, chest.x, chest.y)
        halmaz = self.racs_vilag_chest.get(hely)
        if halmaz is not None:
            halmaz.discard(chest)
            if not halmaz:
                del self.racs_vilag_chest[hely]

    def tank_chestdrop_racsbol_torles(self, chest):
        hely = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, chest.x, chest.y)
        halmaz = self.racs_vilag_chestdrop.get(hely)
        if halmaz is not None:
            halmaz.discard(chest)
            if not halmaz:
                del self.racs_vilag_chestdrop[hely]

    def tank_chest_racsba_rakas(self, chest):
        hely = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, chest.x, chest.y)
        self.racs_vilag_chest[hely[0], hely[1]].add(chest)

    def tank_jatekos_racs_frissit(self, jatekos):
        uj_kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jatekos.x, jatekos.y)

        if getattr(jatekos, "utolso_racs", None) == uj_kulcs:
            return

        self.tank_jatekos_racsbol_torles(jatekos)

        self.racs_vilag_tank_jatekosok[uj_kulcs].add(jatekos.azonosito)
        jatekos.utolso_racs = uj_kulcs

    def lovedek_racs_frisitese_mozgatasa(self, delta_ido):
        racs_meret = self.beallitasok.racsok_nagysaga

        for lovedek in self.lovedekek:
            if not lovedek.el:
                continue


            kov_x = lovedek.x + lovedek.irany_x * lovedek.sebesseg * delta_ido
            kov_y = lovedek.y + lovedek.irany_y * lovedek.sebesseg * delta_ido
            oszlop, sor = self.terkep_tank.csempe_hely(kov_x, kov_y)
            try:
                if self.terkep_tank.racs[sor, oszlop] == 3:
                    for chest in self.chestek:

                        if not isinstance(chest, Chest):
                            continue

                        if not chest.el:
                            continue

                        

                        if chest.cella_x == oszlop and chest.cella_y == sor:
                            Buffok.hp(chest, -lovedek.sebzes)
                            #lovedek.el = False

                            if chest.hp <= 0:
                                chest.el = False
                                chest.kincs_lathato = True
                                self.aktualis_chest_db -=1
                                self.terkep_tank.adott_cella_ertek_atiras(chest.x // self.terkep_tank.CELLA, chest.y // self.terkep_tank.CELLA, 0)
                                x, y = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, chest.x, chest.y)
                                self.racs_vilag_chestdrop[x, y].add(chest)
                                self.tank_chest_racsbol_torles(chest)
                                self.chestek.remove(chest)
                                
                            break
            except:
                pass
            lovedek.mozgas(delta_ido, self._tankos_pozicio_jarhato)

            if not lovedek.el:
                if lovedek.utolso_racs is not None:
                    self.racs_vilag_lovedekek[lovedek.utolso_racs].discard(lovedek)
                continue
            if self.lovedek_talalat_jatekoson_raccsal(lovedek):
                if lovedek.utolso_racs is not None:
                    self.racs_vilag_lovedekek[lovedek.utolso_racs].discard(lovedek)
                continue

            uj_racs = KorSeged.kulcs(racs_meret, lovedek.x, lovedek.y)

            if uj_racs != lovedek.utolso_racs:
                if lovedek.utolso_racs is not None:
                    self.racs_vilag_lovedekek[lovedek.utolso_racs].discard(lovedek)

                self.racs_vilag_lovedekek[uj_racs].add(lovedek)
                lovedek.utolso_racs = uj_racs

        self.lovedekek = [l for l in self.lovedekek if l.el]

    def lovedek_talalat_jatekoson_raccsal(self, lovedek):
        keresesi_sugar = lovedek.sugar + self.beallitasok.jatekos_sugar

        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga,lovedek.x, lovedek.y, keresesi_sugar, 1):
            for jatekos_id in list(self.racs_vilag_tank_jatekosok.get(kulcs, [])):
                jatekos = self.jatekosok.get(jatekos_id)

                if not isinstance(jatekos, Tanki):
                    continue

                if not jatekos.el:
                    continue

                #if jatekos.azonosito == lovedek.tulajdonos_id:
                #    continue

                if KorSeged.korok_utkozne_e(lovedek.x, lovedek.y, lovedek.sugar, jatekos.x, jatekos.y, jatekos.sugar):
                    Buffok.hp(jatekos, -lovedek.sebzes)
                    
                    for j, i in self.jatekosok.items():
                        if i.azonosito == (lovedek.tulajdonos_id):
                            i.talalatok += 1
                            if jatekos.hp <= 0:
                                i.olesek += 1
                    lovedek.el = False

                    if jatekos.hp <= 0:
                        jatekos.el = False
                        self.tank_jatekos_racsbol_torles(jatekos)
                        del self.jatekosok[jatekos.azonosito]

                    return True
        

        return False

    def _lathato_lovedekek(self, kamera_x, kamera_y, szelesseg, magassag):
        bal = kamera_x - self.beallitasok.alma_rajzolas_puffer
        jobb = kamera_x + szelesseg + self.beallitasok.alma_rajzolas_puffer
        fent = kamera_y - self.beallitasok.alma_rajzolas_puffer
        lent = kamera_y + magassag + self.beallitasok.alma_rajzolas_puffer
        start_cx, start_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, bal, fent)
        end_cx, end_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jobb, lent)
        eredmeny = []
        for cx in range(start_cx - 1, end_cx + 2):
            for cy in range(start_cy - 1, end_cy + 2):
                for lovedek in self.racs_vilag_lovedekek.get((cx, cy), []):
                    if bal < lovedek.x < jobb and fent < lovedek.y < lent:
                        eredmeny.append((lovedek.allapot_dict()))
        return eredmeny
    
    def _lathato_chestek(self, kamera_x, kamera_y, szelesseg, magassag):
        bal = kamera_x - self.beallitasok.alma_rajzolas_puffer
        jobb = kamera_x + szelesseg + self.beallitasok.alma_rajzolas_puffer
        fent = kamera_y - self.beallitasok.alma_rajzolas_puffer
        lent = kamera_y + magassag + self.beallitasok.alma_rajzolas_puffer
        start_cx, start_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, bal, fent)
        end_cx, end_cy = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, jobb, lent)
        eredmeny = []
        for cx in range(start_cx - 1, end_cx + 2):
            for cy in range(start_cy - 1, end_cy + 2):
                for chest in self.racs_vilag_chestdrop.get((cx, cy), []):
                    if bal < chest.x < jobb and fent < chest.y < lent and chest.kincs_lathato:
                        eredmeny.append((chest.allapot_dict()))
        return eredmeny

    def tankos_lathato_terkep_resz(self, kamera_x, kamera_y, szelesseg, magassag):
        if self.terkep_tank is None:
            return None

        cella = self.terkep_tank.CELLA
        puffer = 2

        start_oszlop = max(0, int(kamera_x // cella) - puffer)
        end_oszlop = min(
            self.terkep_tank.SZEL,
            int((kamera_x + szelesseg) // cella) + puffer
        )

        start_sor = max(0, int(kamera_y // cella) - puffer)
        end_sor = min(
            self.terkep_tank.MAG,
            int((kamera_y + magassag) // cella) + puffer
        )

        resz = self.terkep_tank.racs[start_sor:end_sor, start_oszlop:end_oszlop]

        return {
            "start_sor": start_sor,
            "start_oszlop": start_oszlop,
            "sor_db": int(end_sor - start_sor),
            "oszlop_db": int(end_oszlop - start_oszlop),
            "cella": int(cella),
            "adatok": resz.tolist()
        }

    def van_fal_ket_pont_kozott(self, x1, y1, x2, y2):
        """True = van fal a két pont között, False = nincs fal."""
    
        oszlop1, sor1 = self.terkep_tank.csempe_hely(x1, y1)
        oszlop2, sor2 = self.terkep_tank.csempe_hely(x2, y2)

        if oszlop1 == oszlop2 and sor1 == sor2:
            return False

        dx = abs(oszlop2 - oszlop1)
        dy = abs(sor2 - sor1)

        sx = 1 if oszlop1 < oszlop2 else -1
        sy = 1 if sor1 < sor2 else -1

        hiba = dx - dy

        aktualis_oszlop = oszlop1
        aktualis_sor = sor1

        while True:
            dupla_hiba = 2 * hiba

            if dupla_hiba > -dy:
                hiba -= dy
                aktualis_oszlop += sx

            if dupla_hiba < dx:
                hiba += dx
                aktualis_sor += sy

            if aktualis_oszlop == oszlop2 and aktualis_sor == sor2:
                return False

            if not self.terkep_tank.jarhato(aktualis_sor, aktualis_oszlop):
                return True
            
    def chest_potlas(self):
        if self.aktualis_chest_db < self.max_chest:
            chest = self.terkep_tank.chest_generalas(self.chest_azonosito)
            if chest is None:
                return
            self.chestek.append(chest)
            self.tank_chest_racsba_rakas(chest)
            self.aktualis_chest_db +=1
            self.chest_azonosito += 1
    # npc

    def _tank_celpont_kereses(self, tank: Tanki):

        legjobb = None
        legjobb_tav = float("inf")

        for masik in self.jatekosok.values():
            if not isinstance(masik, Tanki):
                continue

            if not masik.el:
                continue

            if not masik.jatekos_e:
                continue

            if masik.azonosito == tank.azonosito:
                continue

            tav = KorSeged.tavolsag(tank.x, tank.y, masik.x, masik.y)

            if tav < legjobb_tav:
                legjobb_tav = tav
                legjobb = masik

        return legjobb

    def _tank_celoz_pont_fele(self, tank: Tanki, cel_x, cel_y, delta_ido) :
        fordulasi_sebesseg = getattr(tank, "fordulasi_sebesseg", 180.0)

        dx = cel_x - tank.x
        dy = cel_y - tank.y

        if abs(dx) < 0.001 and abs(dy) < 0.001:
            return

        cel_fok = (math.degrees(math.atan2(dy, dx)) + 90) % 360

        kulonbseg = (cel_fok - tank.fok + 180) % 360 - 180

        max_fordulas = fordulasi_sebesseg * delta_ido

        if kulonbseg > max_fordulas:
            kulonbseg = max_fordulas
        elif kulonbseg < -max_fordulas:
            kulonbseg = -max_fordulas

        tank.fok = (tank.fok + kulonbseg) % 360

    def _tank_mozgas_pont_fele(self, tank: Tanki, cel_x, cel_y, delta_ido, tavolsag_tartas = 80.0) :

        tank.mozog_balra = False
        tank.mozog_jobbra = False
        tank.mozog_fel = False
        tank.mozog_le = False

        tav = KorSeged.tavolsag(tank.x, tank.y, cel_x, cel_y)

        self._tank_celoz_pont_fele(tank, cel_x, cel_y, delta_ido)

        if tav > tavolsag_tartas:
            tank.mozog_fel = True

    def _tank_lovedek_veszely_pont(self, tank: Tanki):
        x, y = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, tank.x, tank.y)
        

        for i in range(-2, 3):
            for j in range(-2, 3):
                j_x = x - i
                j_y = y -j

                for lovedek in self.racs_vilag_lovedekek.get((j_x, j_y), []):
                    if not lovedek.el:
                        continue

                    #if lovedek.tulajdonos_id == tank.azonosito:
                    #    continue

                    rel_x = tank.x - lovedek.x
                    rel_y = tank.y - lovedek.y

                    elore_tav = rel_x * lovedek.irany_x + rel_y * lovedek.irany_y

                    if elore_tav <= 0:
                        continue

                    if elore_tav > 550:
                        continue

                    oldal_tav = abs(rel_x * lovedek.irany_y - rel_y * lovedek.irany_x)

                    veszely_hatar = tank.sugar + lovedek.sugar + 35

                    if oldal_tav > veszely_hatar:
                        continue

                    kit_x = -lovedek.irany_y
                    kit_y = lovedek.irany_x

                    for irany in (1, -1):
                        cel_x = tank.x + kit_x * irany * 180
                        cel_y = tank.y + kit_y * irany * 180

                        if self._tankos_pozicio_jarhato(cel_x, cel_y, tank.sugar):
                            return cel_x, cel_y

        return None

    def _tank_keres_lathato_pontot(self, tank: Tanki, x, y):
        if self.frissitesi_szamlalo % tank.dontes_gyakorisag != tank.dontes_fazis:
            return None

        if self.terkep_tank is None:
            return None


        tud_mozogni = False
        lepes = tank.sugar * 1.0 
        
        iranyok = [
            (0, -lepes), (0, lepes), (-lepes, 0), (lepes, 0),
            (-lepes, -lepes), (lepes, -lepes), (-lepes, lepes), (lepes, lepes)
        ]
        
        for dx, dy in iranyok:
            teszt_x = tank.x + dx
            teszt_y = tank.y + dy
            
            if self._tankos_pozicio_jarhato(teszt_x, teszt_y, tank.sugar):
                if self._tank_pozicio_szabad(tank, teszt_x, teszt_y):
                    tud_mozogni = True
                    break

        if not tud_mozogni:
            return
        cella = self.terkep_tank.CELLA

        start_oszlop, start_sor = self.terkep_tank.csempe_hely(tank.x, tank.y)

        max_tav = 25

        min_sor = max(0, start_sor - max_tav)
        max_sor = min(self.terkep_tank.MAG - 1, start_sor + max_tav)
        min_oszlop = max(0, start_oszlop - max_tav)
        max_oszlop = min(self.terkep_tank.SZEL - 1, start_oszlop + max_tav)

        start = (start_sor, start_oszlop)

        sorban = deque()
        sorban.append(start)

        volt_mar = set()
        volt_mar.add(start)

        honnan_jott = {}

        iranyok = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]
        pontok = []
        while sorban:
            sor, oszlop = sorban.popleft()

            cel_x = oszlop * cella + cella / 2
            cel_y = sor * cella + cella / 2
            


            if not self.van_fal_ket_pont_kozott(cel_x, cel_y, x, y):
                aktualis = (sor, oszlop)

                if not self._tank_pozicio_szabad(tank, cel_x, cel_y):
                    continue

                

                while honnan_jott.get(aktualis) is not None and honnan_jott[aktualis] != start:
                    aktualis = honnan_jott[aktualis]

                lep_sor, lep_oszlop = aktualis

                lep_x = lep_oszlop * cella + cella / 2
                lep_y = lep_sor * cella + cella / 2
                fal_db = self._tank_kornyezo_falak_szama(sor, oszlop)

                pontszam = KorSeged.tavolsag(tank.x, tank.y, cel_x, cel_y) * 10
                pontszam += KorSeged.tavolsag(tank.x, tank.y, lep_x, lep_y) * 2
                pontszam += fal_db * 300
                pontszam += KorSeged.tavolsag(cel_x, cel_y, x, y) * 0.2
                pontok.append((pontszam, lep_x, lep_y))

                #return lep_x, lep_y

            for ds, do in iranyok:
                uj_sor = sor + ds
                uj_oszlop = oszlop + do

                if uj_sor < min_sor or uj_sor > max_sor:
                    continue

                if uj_oszlop < min_oszlop or uj_oszlop > max_oszlop:
                    continue

                kulcs = (uj_sor, uj_oszlop)

                if kulcs in volt_mar:
                    continue

                if not self.terkep_tank.jarhato(uj_sor, uj_oszlop):
                    continue

                uj_x = uj_oszlop * cella + cella / 2
                uj_y = uj_sor * cella + cella / 2

                if not self._tankos_pozicio_jarhato(uj_x, uj_y, tank.sugar+ 15):
                    continue

                volt_mar.add(kulcs)
                honnan_jott[kulcs] = (sor, oszlop)
                sorban.append(kulcs)

        if len(pontok) == 0:
            return None
        
        legkisebb = pontok[0]
    
        legjobb = min(pontok, key=lambda p: p[0])
        return legjobb[1], legjobb[2]


    def _tank_kornyezo_falak_szama(self, sor, oszlop):
        fal_db = 0

        for ds, do in [(-1,0), (1,0), (0,-1), (0,1)]:
            if not self.terkep_tank.jarhato(sor + ds, oszlop + do):
                fal_db += 1

        return fal_db

    def tank_npc_mozgatas_loves(self, delta_ido):
        lotav = 1100.0
        idealis_lotav = 700.0
        self.frissitesi_szamlalo += 1

        for tank in list(self.jatekosok.values()):
            if not isinstance(tank, Tanki):
                continue
            if not tank.el:
                continue
            if tank.jatekos_e:
                continue

            tank.mozog_balra = False
            tank.mozog_jobbra = False
            tank.mozog_fel = False
            tank.mozog_le = False
            tank.loves = False

            kitero_pont = self._tank_lovedek_veszely_pont(tank)

            if kitero_pont is not None:
                tank.alapot = "kitero"
                self._tank_mozgas_pont_fele(
                    tank,
                    kitero_pont[0],
                    kitero_pont[1],
                    delta_ido,
                    tavolsag_tartas=10.0
                )
                continue

            celpont = self._tank_celpont_kereses(tank)

            if celpont is None:
                tank.alapot = "jarorozes"
                self.jarorozes(tank, delta_ido)
                continue

            tav = KorSeged.tavolsag(tank.x, tank.y, celpont.x, celpont.y)
            van_fal = self.van_fal_ket_pont_kozott(
                tank.x,
                tank.y,
                celpont.x,
                celpont.y
            )

            if tav <= lotav and not van_fal:
                tank.alapot = "tamadas"

                self._tank_celoz_pont_fele(tank, celpont.x, celpont.y, delta_ido)

                tank.loves = True

                if tav > idealis_lotav:
                    tank.mozog_fel = True

                continue

            tank.alapot = "vadaszat"

            lathato_pont = self._tank_keres_lathato_pontot(tank, celpont.x, celpont.y)

            if lathato_pont is not None:
                self._tank_mozgas_pont_fele(tank, lathato_pont[0], lathato_pont[1], delta_ido, tavolsag_tartas=40.0)
            else:
                self._tank_mozgas_pont_fele(tank, celpont.x, celpont.y, delta_ido, tavolsag_tartas=idealis_lotav)
            
    def jarorozes(self, tank, delta_ido):
        if not isinstance(tank, Tanki):
            return
        if not tank.el:
            return
        if tank.jatekos_e:
            return
        if self.terkep_tank is None:
            return

        cella = self.terkep_tank.CELLA
        
        

        if tank.jaror_cel_kordinata is None:
            tank.jarorozes_figyelo["ido"] = 0.0
            tank_oszlop, tank_sor = self.terkep_tank.csempe_hely(tank.x, tank.y)

            for _ in range(80):
                sor = random.randint(tank_sor - 10, tank_sor + 10)
                oszlop = random.randint(tank_oszlop - 10, tank_oszlop + 10)

                if sor < 1 or sor >= self.terkep_tank.MAG - 1:
                    continue

                if oszlop < 1 or oszlop >= self.terkep_tank.SZEL - 1:
                    continue

                if not self.terkep_tank.jarhato(sor, oszlop):
                    continue

                cel_x = oszlop * cella + cella / 2
                cel_y = sor * cella + cella / 2

                if not self._tankos_pozicio_jarhato(cel_x, cel_y, tank.sugar):
                    continue

                tank.jaror_cel_kordinata = (sor, oszlop)
                break

            if tank.jaror_cel_kordinata is None:
                return
        
        tank.jarorozes_figyelo["ido"] += delta_ido

        if tank.jarorozes_figyelo["ido"] >= 1.0:
            regi = tank.jarorozes_figyelo["kordinata"]

            if regi is not None:
                mozgas = KorSeged.tavolsag(tank.x, tank.y, regi[0], regi[1])

                if mozgas < 5:
                    tank.jaror_cel_kordinata = None

            tank.jarorozes_figyelo["kordinata"] = (tank.x, tank.y)
            tank.jarorozes_figyelo["ido"] = 0.0
            return


        cel_sor, cel_oszlop = tank.jaror_cel_kordinata

        cel_x = cel_oszlop * cella + cella / 2
        cel_y = cel_sor * cella + cella / 2

        if KorSeged.tavolsag(tank.x, tank.y, cel_x, cel_y) < 45:
            tank.jaror_cel_kordinata = None
            return

        if not self.van_fal_ket_pont_kozott(tank.x, tank.y, cel_x, cel_y):
            self._tank_mozgas_pont_fele(
                tank,
                cel_x,
                cel_y,
                delta_ido,
                tavolsag_tartas=40.0
            )
            return

        kovetkezo_pont = self._tank_keres_lathato_pontot(tank, cel_x, cel_y)

        if kovetkezo_pont is not None:
            self._tank_mozgas_pont_fele(
                tank,
                kovetkezo_pont[0],
                kovetkezo_pont[1],
                delta_ido,
                tavolsag_tartas=40.0
            )
        else:
            tank.jaror_cel_kordinata = None

    def _tank_pozicio_szabad(self, tank, x, y, puffer=8):
        keresesi_sugar = tank.sugar * 2 + puffer

        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, x, y, keresesi_sugar, 1):
            for masik_id in self.racs_vilag_tank_jatekosok.get(kulcs, []):
                if masik_id == tank.azonosito:
                    continue

                masik = self.jatekosok.get(masik_id)

                if not isinstance(masik, Tanki):
                    continue
                if not masik.el:
                    continue

                minimum_tav = tank.sugar + masik.sugar + puffer

                if KorSeged.tavolsag(x, y, masik.x, masik.y) < minimum_tav:
                    return False

        return True
        
    # ----------------------------- CSAK platformeres MÓD -----------------------------
    def _platformer_frissites(self, delta_ido):
        for jatekos in self.jatekosok.values():
            self.jatekos_mozgas(jatekos, delta_ido)
            jatekos.eltelt_ido += delta_ido
            

    def platformer_kezdes(self, jelenlegi_szoba=None):
        self.platformer_file_helye = os.path.join(os.path.dirname(__file__), "platformer_szobak")

        self.jelenlegi_szoba = jelenlegi_szoba
        self.platformer_terkep = None

        self.platformer_spone_point = {}
        self.platformer_szoba_valtas = False

        self.platformer_terkep_betolto(self.jelenlegi_szoba)


    def platformer_terkep_betolto(self, szoba=None):
        fajl = os.path.join(os.path.dirname(__file__), "p1.ldtk")

        self.platformer_terkep = ldtk_terkep_betoltes(
            fajl,
            szoba if szoba else None
        )

        self.jelenlegi_szoba = self.platformer_terkep["szoba"]

        self.beallitasok.vilag_szelesseg = self.platformer_terkep["width"]
        self.beallitasok.vilag_magassag = self.platformer_terkep["height"]

    def jatekos_mozgas(self, jatekos: P_elolenyek, delta_ido):
        bottom_y = jatekos.y 
        higtest_y = jatekos.y - jatekos.height
        midle_1_y = jatekos.y - jatekos.height // 5 * 2
        midle_2_y = jatekos.y - jatekos.height // 5 * 4
        bottom_left_x = jatekos.x
        bottom_right_x = jatekos.x + jatekos.width
        racs_meret = self.platformer_terkep["platform_racs_meret"]
        platform_racs = self.platformer_terkep["platform_racs"]
        

        jatekos.acc.x = 0
        ugras, eses, balra, jobbra = False, False, False, False

        if jatekos.mozog_balra:
            jatekos.acc.x = -self.acc * delta_ido * self.beallitasok.platformer_jatekos_mozgas_szorzo
            balra = True
        if jatekos.mozog_jobbra:
            jatekos.acc.x = self.acc * delta_ido * self.beallitasok.platformer_jatekos_mozgas_szorzo
            jobbra = True
        if jatekos.mozog_balra and jatekos.mozog_jobbra:
            jatekos.acc.x = 0
            balra, jobbra = False, False

        racs_meret = self.platformer_terkep["platform_racs_meret"]
        platform_racs = self.platformer_terkep["platform_racs"]

        puffer = racs_meret * 2
        min_cella_x = int((jatekos.pos.x - puffer) // racs_meret)
        max_cella_x = int((jatekos.pos.x + jatekos.width + puffer) // racs_meret)
        min_cella_y = int((jatekos.pos.y - puffer) // racs_meret)
        max_cella_y = int((jatekos.pos.y + jatekos.height + puffer) // racs_meret)

        szilard_testek = []

        for cella_y in range(min_cella_y, max_cella_y + 1):
            for cella_x in range(min_cella_x, max_cella_x + 1):
                block = platform_racs.get((cella_x, cella_y))
                if block is not None:
                    szilard_testek.append(block)

        if jatekos.jump and jatekos.dare_i_jump:
            jatekos.vel.y = self.beallitasok.platformer_ugras
            jatekos.dare_i_jump = False
            jatekos.can_i_jump = True
        elif not jatekos.jump and jatekos.vel.y <0 and jatekos.can_i_jump:
            jatekos.vel.y *= 0.5
            jatekos.can_i_jump = False
        """elif jatekos.jump and jatekos.jumping <= 10 and jatekos.vel.y < 0 and jatekos.can_i_jump:
            jatekos.jumping_szamlalo += 1
            if jatekos.jumping_szamlalo % 1 == 0:
                jatekos.jumping += 1
        else:
            if jatekos.jumping >= 10:
                string = "1.0"# + str(jatekos.jumping)[-1]
            else: string = "0." + str(jatekos.jumping)
            if string == "0.0":
                pass
            else:
                jatekos.vel.y = jatekos.vel.y*float(string)
                print("ugrot")
                print(string)
                jatekos.jumping = 0
                jatekos.jumping_szamlalo=0
                jatekos.can_i_jump = False"""

        if -6 <= jatekos.vel.y <= 1:
            self.gravitacio  = max(self.gravitacio - 0.1, 0.5)
        else: self.gravitacio = min(self.gravitacio+0.1, self.alap_gravitacio)


        



        jatekos.vel.y = min(jatekos.vel.y + self.gravitacio, self.max_gravitacio)

        jatekos.acc.x -= jatekos.vel.x * self.gyorsulas_csokentes
        jatekos.vel.x += jatekos.acc.x
        jatekos.pos.x += jatekos.vel.x  

        for block in szilard_testek:
            bx, by, bw, bh = block.get("x"), block.get("y"), block.get("width"), block.get("height")
            
            
            if (jatekos.pos.x < bx + bw and jatekos.pos.x + jatekos.width > bx and jatekos.pos.y < by + bh and jatekos.pos.y + jatekos.height > by):
                
                if jatekos.vel.x > 0: 
                    jatekos.pos.x = bx - jatekos.width
                    jatekos.vel.x = 0
                    jobbra = False
                elif jatekos.vel.x < 0:  
                    jatekos.pos.x = bx + bw
                    jatekos.vel.x = 0
                    balra = False

       
        jatekos.vel.y += jatekos.acc.y
        jatekos.pos.y += jatekos.vel.y  

        for block in szilard_testek:
            bx, by, bw, bh = block.get("x"), block.get("y"), block.get("width"), block.get("height")
            
            if (jatekos.pos.x < bx + bw and jatekos.pos.x + jatekos.width > bx and jatekos.pos.y < by + bh and jatekos.pos.y + jatekos.height > by):
                
                if jatekos.vel.y > 0:
                    jatekos.pos.y = by - jatekos.height
                    jatekos.vel.y = 0
                    jatekos.dare_i_jump = True
                
                elif jatekos.vel.y < 0:
                    jatekos.pos.y = by + bh
                    jatekos.vel.y = 0

        if jatekos.vel.y != 0:
            jatekos.dare_i_jump = False
        
        jatekos.x = jatekos.pos.x
        jatekos.y = jatekos.pos.y
        jatekos.akcio = []

        if ugras or jatekos.vel.y < 0:
            jatekos.akcio = "Jump Start"
        elif eses or jatekos.vel.y > 0:
            jatekos.akcio = "Falling Down"
        #else:
        #    jatekos.akcio = "Idle"
        #if jobbra and balra or not balra and not jobbra and not ugras:
            #jatekos.irany = 0
        if jobbra:
            jatekos.irany = 1
        elif balra:
            jatekos.irany = -1

        jatekos.kamera.mozgas(jatekos.x, jatekos.y, jatekos.width, jatekos.height, jatekos.irany)


        jatekos.utes = jatekos.attack
        if jatekos.tamadas(delta_ido):
            jatekos.tamadas_id += 1
            kozep_x = jatekos.x + jatekos.width / 2
            kozep_y = jatekos.y - jatekos.height / 2
 
            if jatekos.mozog_fel and not jatekos.mozog_le:
                hitbox_x = kozep_x - jatekos.tamadas_szelesseg / 2
                hitbox_y = jatekos.y - jatekos.height - jatekos.tamadas_magassag
            elif jatekos.mozog_le and not jatekos.mozog_fel:
                hitbox_x = kozep_x - jatekos.tamadas_szelesseg / 2
                hitbox_y = jatekos.y
            else:
                if jatekos.irany == -1:
                    hitbox_x = jatekos.x - jatekos.tamadas_szelesseg
                else:
                    hitbox_x = jatekos.x + jatekos.width
                hitbox_y = kozep_y - jatekos.tamadas_magassag / 2
 
            for masik in self.jatekosok.values():
                if masik.azonosito == jatekos.azonosito:
                    continue
                if not masik.el:
                    continue
 
                if KorSeged.dobozok_utkozne_e(hitbox_x, hitbox_y, jatekos.tamadas_szelesseg, jatekos.tamadas_magassag, masik.x, masik.y - masik.height, masik.width, masik.height,):
                    Buffok.hp(masik, -jatekos.tamadas_sebzes)
                    jatekos.talalatok += 1
                    if masik.hp <= 0:
                        jatekos.olesek += 1


def kodbol_port(kod, beallitasok = None):
    b = beallitasok or Beallitasok()
    szam = int(kod)
    return b.szerver_alap_port + (szam % b.szerver_port_tartomany)
