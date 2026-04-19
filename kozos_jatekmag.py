import math
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Iterable


class Beallitasok:
    def __init__(self):
        self.vilag_szelesseg = 10000  # A teljes pálya szélessége világ-koordinátában.
        self.vilag_magassag = 10000  # A teljes pálya magassága világ-koordinátában.
        self.racsok_nagysaga = 200  # A ritkított térbeli rács cellamérete gyors keresésekhez.
        self.fps = 30  # A kliens cél képkockaszáma.
        self.szerver_fps = 30  # A szerver cél frissítési frekvenciája.

        self.kigyó_sugár = 20  # A kígyó egy testpontjának sugara.
        self.kigyo_alap_hossz = 4  # A kígyó induló testpontjainak száma.
        self.kigyo_resz_tav = 28  # Az ideális távolság két egymást követő testpont között.
        self.kigyo_novekedes_alma_db = 1  # Egy alma után ennyi növekedési egységet kap a kígyó.
        self.kigyo_no = 3  # Ennyi alma-növekedési egység után nő egy teljes testponttal a kígyó.
        self.kigyo_rajzolas_puffer = 100  # A képernyőn kívül még ennyi ráhagyással rajzolunk kígyót.
        self.kigyo_lathato_pont_limit = 350  # Ennyi testpontot küldünk át maximum hálózaton egy kígyóról.
        self.kigyo_utkozes_szorzo = 1.75  # Kígyófej és másik kör ütközési küszöbszorzója.
        self.kigyo_onvedo_index = 3  # Saját fejhez közeli ennyi pontot kihagyunk önütközésnél.
        self.kigyo_dontesi_szogek = [-60, -45, -30, -15, 0, 15, 30, 45, 60]  # AI lehetséges irányszögei.
        self.kigyo_veszely_puffer = 3.0  # Falakhoz és testekhez tartott biztonsági puffer a kígyó AI-nak.
        self.kigyo_lato_ido = 60  # Ennyi jövőbeli lépést becsül meg a kígyó AI.
        self.kigyo_max_memoria_szorzo = 6  # Ennyiszeres pufferrel tároljuk a kígyó útvonalpontjait.
        self.kigyo_respawn_varakozas = 24  # Ennyi frissítésenként pótoljuk az AI kígyókat.
        self.kigyo_spawn_puffer = 320  # Új kígyó ennyinél közelebb ne szülessen játékoshoz.

        self.alma_size = 25  # Egy alma négyzetének oldalmérete.
        self.alma_kor_sugár = 12.5  # Az alma közelítő köre ütközéshez.
        self.alma_maximum = 6000  # A pályán egyszerre tartható almák felső korlátja.
        self.alma_potlasi_limit = 50  # Egy frissítésben maximum ennyi új almát rakunk le.
        self.alma_lathato_limit = 700  # Hálózatra egyszerre ennyi almát küldünk legfeljebb.
        self.alma_rajzolas_puffer = 60  # A képernyőn kívül még ennyi ráhagyással rajzolunk almát.

        self.jatekos_sugar = 25  # A pattogós játékos köreinek sugara.
        self.jatekos_sebesseg = 10.0 * self.fps # A pattogós játékos alap mozgási sebessége.
        self.jatekos_hp = 3  # A pattogós játékos induló élete.
        self.jatekos_utkozes_puffer = 2.0  # Pattogós körök minimális szétválasztási ráhagyása.

        self.patogo_sugar = 40  # A pattogó ellenségek sugara.
        self.patogo_min_sebesseg = 3.0 * self.fps # A pattogó ellenség minimális komponens-sebessége.
        self.patogo_max_sebesseg = 4.0 * self.fps # A pattogó ellenség maximális komponens-sebessége.
        self.patogo_rajzolas_puffer = 100  # Pattogó objektumok rajzolási ráhagyása.

        self.pause_gomb_szelesseg = 200  # A pause gomb szélessége.
        self.pause_gomb_magassag = 50  # A pause gomb magassága.

        self.szoba_kod_hossz = 5  # A létrehozott LAN szobakód hossza.
        self.szerver_alap_port = 20000  # A szobakódokból képzett portok alsó határa.
        self.szerver_port_tartomany = 30000  # A szobakód -> port képzéshez használt tartomány.
        self.felfedezo_port = 37021  # A LAN felfedező UDP portja.
        self.felfedezo_valasz_ido = 2.5  # Ennyi másodpercig vár a kliens LAN válaszra.
        
        self.dontes_gyakorisag = 5
        self.kigyo_max_fordulas_fok = 40
        self.top_hany = 5


class KorSeged:
    @staticmethod
    def tavolsag(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def normalizal(dx: float, dy: float) -> Tuple[float, float]:
        hossz = math.hypot(dx, dy)
        if hossz < 1e-6:
            return 0.0, 0.0
        return dx / hossz, dy / hossz

    @staticmethod
    def korok_utkozne_e(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float) -> bool:
        return math.hypot(x2 - x1, y2 - y1) < (r1 + r2)

    @staticmethod
    def kulcs(racsok_nagysaga: int, x: float, y: float) -> Tuple[int, int]:
        return int(x // racsok_nagysaga), int(y // racsok_nagysaga)

    @staticmethod
    def szomszed_kulcsok(racsok_nagysaga: int, x: float, y: float, sugar: float, extra: int = 1) -> Iterable[Tuple[int, int]]:
        cx, cy = KorSeged.kulcs(racsok_nagysaga, x, y)
        raszter = max(1, int(math.ceil(sugar / racsok_nagysaga))) + extra
        for rx in range(cx - raszter, cx + raszter + 1):
            for ry in range(cy - raszter, cy + raszter + 1):
                yield rx, ry


class SzinSeged:
    @staticmethod
    def veletlen_szin() -> Tuple[int, int, int]:
        return random.randint(20, 255), random.randint(20, 255), random.randint(20, 255)

    @staticmethod
    def fej_szin(szin: Tuple[int, int, int]) -> Tuple[int, int, int]:
        return min(255, szin[0] + 40), min(255, szin[1] + 40), min(255, szin[2] + 40)


class PattogoJatekos:
    def __init__(self, azonosito: str, nev: str, szin: Tuple[int, int, int], x: float, y: float, beallitasok: Beallitasok):
        self.azonosito = azonosito  # A hálózati vagy helyi játékos egyedi azonosítója.
        self.nev = nev  # A játékos megjelenített neve.
        self.szin = szin  # A játékos köreinek rajzolási színe.
        self.x = x  # A játékos közeppontjának világkoordinátás X helye.
        self.y = y  # A játékos közeppontjának világkoordinátás Y helye.
        self.sugar = beallitasok.jatekos_sugar  # A pattogós játékos ütközési sugara.
        self.sebesseg = beallitasok.jatekos_sebesseg  # A pattogós játékos mozgási sebessége.
        self.hp = beallitasok.jatekos_hp  # A pattogós játékos aktuális életereje.
        self.el = True  # Jelzi, hogy a pattogós játékos életben van-e.
        self.mozog_balra = False  # A bal irányú mozgás szándékát tárolja.
        self.mozog_jobbra = False  # A jobb irányú mozgás szándékát tárolja.
        self.mozog_fel = False  # A felfelé mozgás szándékát tárolja.
        self.mozog_le = False  # A lefelé mozgás szándékát tárolja.

    def allapot_dict(self) -> dict:
        return {
            "azonosito": self.azonosito,
            "nev": self.nev,
            "szin": self.szin,
            "x": self.x,
            "y": self.y,
            "sugar": self.sugar,
            "hp": self.hp,
            "el": self.el,
        }


class PattogoEllenseg:
    def __init__(self, nev: str, x: float, y: float, dx: float, dy: float, beallitasok: Beallitasok):
        self.nev = nev  # A pattogó ellenség egyedi neve vagy sorszáma.
        self.x = x  # A pattogó ellenség középpontjának X koordinátája.
        self.y = y  # A pattogó ellenség középpontjának Y koordinátája.
        self.dx = dx  # A pattogó ellenség vízszintes sebesség-komponense.
        self.dy = dy  # A pattogó ellenség függőleges sebesség-komponense.
        self.sugar = beallitasok.patogo_sugar  # A pattogó ellenség köreinek sugara.
        self.el = True  # Jelzi, hogy az ellenség aktív-e.

    def allapot_dict(self) -> dict:
        return {
            "nev": self.nev,
            "x": self.x,
            "y": self.y,
            "sugar": self.sugar,
        }


class KigyoAdat:
    def __init__(self, azonosito: str, nev: str, szin: Tuple[int, int, int], nehezseg_szint: str, fej_x: float, fej_y: float, beallitasok: Beallitasok, jatekos_e: bool = False):
        self.azonosito = azonosito  # A kígyó egyedi azonosítója, szerveren vagy kliensen ezzel különböztetjük meg.
        self.nev = nev  # A kígyó megjelenített neve.
        self.szin = szin  # A kígyó testszíne.
        self.fej_szin = SzinSeged.fej_szin(szin)  # A kígyó fejének kiemelt színe.
        self.nehezseg_szint = nehezseg_szint  # A kígyóhoz tartozó nehézségi profil neve.
        self.jatekos_e = jatekos_e  # Jelzi, hogy emberi vagy AI vezérelt kígyóról van-e szó.
        self.el = True  # Jelzi, hogy a kígyó él-e.
        self.olesek = 0  # A kígyó által szerzett ölések száma.
        self.alma_pontok = 0  # Az elfogyasztott almák száma.
        self.sugar = beallitasok.kigyó_sugár  # A kígyó minden testpontjának sugara.
        self.resz_tav = beallitasok.kigyo_resz_tav  # A kígyótest ideális követési távolsága.
        self.irany_x = 1.0  # A kígyó aktuális vízszintes mozgásiránya.
        self.irany_y = 0.0  # A kígyó aktuális függőleges mozgásiránya.
        self.alap_sebesseg = 7.0  # A kígyó alap mozgási sebessége a nehézség szerint.
        self.sebesseg = 7.0  # Az aktuális sebesség, gyorsítás idején eltérhet az alaptól.
        self.cel_sebesseg = 7.0  # A fokozatos gyorsuláshoz használt célsebesség.
        self.no = beallitasok.kigyo_no  # Ennyi növekedési egység után nő egy testponttal.
        self.nosz = 0  # Az összegyűjtött növekedési egységek száma.
        self.osztas = 2  # A régi logikából megőrzött ideális követési mintavétel.
        self.aktualis_osztas = 2.0  # A fokozatos sebességváltás kisimítására használt változó.
        self.idealis_tavolsag = float(self.resz_tav)  # A testkövetés cél-távolsága.
        self.utvonal = []  # A fej korábbi pontjai, ebből követik a testrészek az előzőt.
        self.test_pontok = []  # A kígyó összes testpontja világkoordinátában.
        self.dontes_idozito = 0  # Az AI újratervezésének időzítője.
        self.dontes_gyakorisag = beallitasok.dontes_gyakorisag  # Ennyi frissítésenként számol új AI irányt.
        self.allapot = "vadaszat"  # A jelenlegi AI állapot neve.
        self.celpont = None  # Az AI által célba vett pozíció.
        self.csapda_mod = False  # Fenntartott állapot a későbbi bekerítő viselkedéshez.
        self.szerep = "uldozo"  # Hell nehézségnél kiosztott szerepkör.
        self.gyorsit = False  # Emberi kígyónál jelzi, hogy gyorsítás aktív-e.
        self.utolso_racs = []
        self.dontes_fazis = 0
        self.beallitasok = beallitasok

        self._nehezseg_beallitas(nehezseg_szint, beallitasok)
        self._letrehoz_indulo_test(fej_x, fej_y, beallitasok)

    def _nehezseg_beallitas(self, nehezseg_szint: str, beallitasok: Beallitasok) -> None:
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

    def _letrehoz_indulo_test(self, fej_x: float, fej_y: float, beallitasok: Beallitasok) -> None:
        self.test_pontok = []
        for index in range(beallitasok.kigyo_alap_hossz):
            self.test_pontok.append([fej_x - index * self.idealis_tavolsag, fej_y])
        self.utvonal = [list(self.test_pontok[0])]

    def novekedes(self, beallitasok: Beallitasok) -> None:
        self.nosz += beallitasok.kigyo_novekedes_alma_db
        cel_hossz = beallitasok.kigyo_alap_hossz + (self.nosz // self.no)
        while len(self.test_pontok) < cel_hossz:
            utolso_x, utolso_y = self.test_pontok[-1]
            self.test_pontok.append([utolso_x, utolso_y])

    def beallit_irany(self, dx: float, dy: float) -> None:
        ndx, ndy = KorSeged.normalizal(dx, dy)
        if abs(ndx) > 1e-6 or abs(ndy) > 1e-6:
            self.irany_x = ndx
            self.irany_y = ndy

    def fej_pozicio(self) -> Tuple[float, float]:
        return self.test_pontok[0][0], self.test_pontok[0][1]

    def allapot_dict(self, kamera_x: Optional[float] = None, kamera_y: Optional[float] = None, szelesseg: Optional[int] = None, magassag: Optional[int] = None, puffer: float = 100.0, pont_limit: Optional[int] = None) -> dict:
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
            "alma_pontok": self.alma_pontok,
            "sugar": self.sugar,
            "jatekos_e": self.jatekos_e,
            "ossz_testhosz": len(self.test_pontok)
        }


class VilagAllapot:
    def __init__(self, beallitasok: Optional[Beallitasok] = None, jatek_mode: str = "alma", nehezseg_szint: str = "Normal"):
        self.beallitasok = beallitasok or Beallitasok()  # A közös, minden játékmód által használt konfiguráció.
        self.jatek_mode = jatek_mode  # Az aktuális játékmód neve: alma vagy patogos.
        self.nehezseg_szint = nehezseg_szint  # Az aktuális nehézségi szint neve.
        self.racs_vilag_alma: Dict[Tuple[int, int], List[Tuple[float, float]]] = defaultdict(list)  # A ritkított rácsban tárolt almák listája.
        self.racs_vilag_patog: Dict[Tuple[int, int], List[str]] = defaultdict(list)  # A pattogó ellenségek rács-regisztere név szerint.
        self.racs_vilag_kigyo: Dict[Tuple[int, int], List[Tuple[str, int, float, float, float]]] = defaultdict(list)  # A kígyótestpontok rács-regisztere ütközéshez.
        self.jatekosok: Dict[str, object] = {}  # Az emberi játékosok szótára, módtól függően külön típusú objektumokkal.
        self.kigyo_ellenseg: List[KigyoAdat] = []  # Az almás mód AI kígyóinak listája.
        self.patog_ellenseg: List[PattogoEllenseg] = []  # A pattogós mód ellenségeinek listája.
        self.max_kigyok = 0  # Az adott nehézségi szinthez tartozó cél AI kígyó darabszám.
        self.max_patogok = 0  # Az adott nehézségi szinthez tartozó cél pattogó darabszám.
        self.eddigi_kigyok = 0  # Folyamatos sorszámláló az új AI kígyókhoz.
        self.eddigi_patogok = 0  # Folyamatos sorszámláló az új pattogó ellenségekhez.
        self.kigyo_respawn_idozito = 0  # Az AI kígyó visszatöltési időzítője.
        self.alma_potlasi_idozito = 0  # Az alma pótlás ritmusa.
        self.veletlen = random.Random()  # Saját véletlen generátor a világ logikájához.
        self.dontes_kiosztas = 0
        self.frissitesi_szamlalo = 0
        self.max_frisitesi_szamolo = self.beallitasok.dontes_gyakorisag
        self.uj_jatek(jatek_mode, nehezseg_szint)

    def uj_jatek(self, jatek_mode: str, nehezseg_szint: str) -> None:
        self.jatek_mode = jatek_mode
        self.nehezseg_szint = nehezseg_szint
        self.racs_vilag_alma.clear()
        self.racs_vilag_patog.clear()
        self.racs_vilag_kigyo.clear()
        self.jatekosok = {}
        self.kigyo_ellenseg = []
        self.patog_ellenseg = []
        self.eddigi_kigyok = 0
        self.eddigi_patogok = 0
        self.kigyo_respawn_idozito = 0
        self.alma_potlasi_idozito = 0
        self.max_kigyok = self.kigyo_celszam(nehezseg_szint)
        self.max_patogok = self.patogo_celszam(nehezseg_szint)
        if self.jatek_mode == "alma":
            self._almak_generalasa(self._kezdo_alma_db())
            self._ai_kigyok_potlas(self.max_kigyok)
        else:
            self._pattogok_potlas(self.max_patogok)

    def kigyo_celszam(self, nehezseg_szint: str) -> int:
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

    def patogo_celszam(self, nehezseg_szint: str) -> int:
        if nehezseg_szint == "Easy":
            return 50
        if nehezseg_szint == "Normal":
            return 100
        if nehezseg_szint == "Hard":
            return 150
        if nehezseg_szint == "Nightmare":
            return 200
        if nehezseg_szint == "Hell":
            return 260
        return 100

    def _kezdo_alma_db(self) -> int:
        if self.nehezseg_szint == "Easy":
            return 2000
        if self.nehezseg_szint == "Normal":
            return 3000
        if self.nehezseg_szint == "Hard":
            return 4000
        if self.nehezseg_szint == "Nightmare":
            return 5000
        return 6000

    def _szoba_pozicio_biztonsagos(self, sugar: float, mi: str = "") -> Tuple[float, float]:
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
            else:
                jo = True
                for jatekos in self.jatekosok.values():
                    if KorSeged.korok_utkozne_e(x, y, sugar, jatekos.x, jatekos.y, jatekos.sugar + 30):
                        jo = False
                        break
                if jo:
                    for pattogo in self.patog_ellenseg:
                        if KorSeged.korok_utkozne_e(x, y, sugar, pattogo.x, pattogo.y, pattogo.sugar + 30):
                            jo = False
                            break
                if jo:
                    return float(x), float(y)
        return float(self.veletlen.randint(200, self.beallitasok.vilag_szelesseg - 200)), float(self.veletlen.randint(200, self.beallitasok.vilag_magassag - 200))

    def jatekos_hozzaadasa(self, azonosito: str, nev: str, szin: Tuple[int, int, int]) -> None:
        if self.jatek_mode == "alma":
            x, y = self._szoba_pozicio_biztonsagos(self.beallitasok.kigyó_sugár, "kigyo")
            uj = KigyoAdat(azonosito, nev, szin, self.nehezseg_szint, x, y, self.beallitasok, True)
            self.jatekosok[azonosito] = uj
            self.racs_kigyo_hozzaad(uj)
        else:
            x, y = self._szoba_pozicio_biztonsagos(self.beallitasok.jatekos_sugar, "patogos")
            self.jatekosok[azonosito] = PattogoJatekos(azonosito, nev, szin, x, y, self.beallitasok)

    def jatekos_torlese(self, azonosito: str) -> None:
        jatekos = self.jatekosok.get(azonosito)

        if isinstance(jatekos, KigyoAdat):
            self._kigyo_racsbol_torles(jatekos)

        if azonosito in self.jatekosok:
            self.kigyo_to_almak([self.jatekosok[azonosito]])
            del self.jatekosok[azonosito]

    def jatekos_irany_beallitasa(self, azonosito: str, dx: float, dy: float) -> None:
        if self.jatek_mode != "alma":
            return
        kigyo = self.jatekosok.get(azonosito)
        if isinstance(kigyo, KigyoAdat):
            kigyo.beallit_irany(dx, dy)

    def jatekos_gyorsitas_beallitasa(self, azonosito: str, gyors: bool) -> None:
        if self.jatek_mode != "alma":
            return
        kigyo = self.jatekosok.get(azonosito)
        if isinstance(kigyo, KigyoAdat):
            kigyo.gyorsit = gyors
            kigyo.cel_sebesseg = kigyo.alap_sebesseg * 2.0 if gyors else kigyo.alap_sebesseg

    def pattogos_mozgas_beallitasa(self, azonosito: str, balra: bool, jobbra: bool, fel: bool, le: bool) -> None:
        if self.jatek_mode != "patogos":
            return
        jatekos = self.jatekosok.get(azonosito)
        if isinstance(jatekos, PattogoJatekos):
            jatekos.mozog_balra = balra
            jatekos.mozog_jobbra = jobbra
            jatekos.mozog_fel = fel
            jatekos.mozog_le = le

    def ujrainditas(self, adatok):
        if isinstance(adatok, tuple):
            azonosito, nev, szin = adatok
            #if azonosito not in self.jatekosok:
            #   return
            try:
                self.jatekos_torlese(azonosito)
            except:
                pass
            self.jatekos_hozzaadasa(azonosito, nev, szin)
            
        
            
        #if azonosito in self.jatekosok:
         #   pass
            
            #nev = self.jatekosok[azonosito].nev
            #szin = self.jatekosok[azonosito].szin
            

            
        else:
            azonosito = adatok.azonosito
            nev = adatok.nev
            szin = adatok.szin
            self.jatekos_torlese(azonosito)
            self.jatekos_hozzaadasa(azonosito, nev, szin)

    def frissites(self, delta_ido) -> None:
        if self.jatek_mode == "alma":
            self._alma_mod_frissites(delta_ido)
        else:
            self._patogos_mod_frissites(delta_ido)

    def _almak_generalasa(self, mennyiseg: int) -> None:
        jelenlegi = self.almak_szama()
        cel = min(self.beallitasok.alma_maximum, jelenlegi + mennyiseg)
        while self.almak_szama() < cel:
            x = self.veletlen.randint(50, self.beallitasok.vilag_szelesseg - 50)
            y = self.veletlen.randint(50, self.beallitasok.vilag_magassag - 50)
            kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, x, y)
            if not self._alma_tul_kozel(x, y):
                self.racs_vilag_alma[kulcs].append((float(x), float(y)))

    def _alma_tul_kozel(self, x: float, y: float) -> bool:
        sugar = self.beallitasok.alma_size * 1.4
        for kulcs in KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, x, y, sugar, 1):
            for ax, ay in self.racs_vilag_alma.get(kulcs, []):
                if KorSeged.korok_utkozne_e(x, y, self.beallitasok.alma_kor_sugár, ax, ay, self.beallitasok.alma_kor_sugár):
                    return True
        return False

    def almak_szama(self) -> int:
        return sum(len(ertek) for ertek in self.racs_vilag_alma.values())

    def _ai_kigyok_potlas(self, mennyiseg: int) -> None:
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

    def _pattogok_potlas(self, mennyiseg: int) -> None:
        for _ in range(mennyiseg):
            self.eddigi_patogok += 1
            x, y = self._szoba_pozicio_biztonsagos(self.beallitasok.patogo_sugar, "patogos")
            dx = self.veletlen.choice([-1, 1]) * self.veletlen.uniform(self.beallitasok.patogo_min_sebesseg, self.beallitasok.patogo_max_sebesseg)
            dy = self.veletlen.choice([-1, 1]) * self.veletlen.uniform(self.beallitasok.patogo_min_sebesseg, self.beallitasok.patogo_max_sebesseg)
            self.patog_ellenseg.append(PattogoEllenseg(f"Patogo_{self.eddigi_patogok}", x, y, dx, dy, self.beallitasok))
        
    def _kigyo_racs_rekord_index(self, cella_lista, azonosito: str, index: int) -> int:
        for poz, rekord in enumerate(cella_lista):
            rekord_azonosito, rekord_index, _, _, _ = rekord
            if rekord_azonosito == azonosito and rekord_index == index:
                return poz
        return -1

    def _kigyo_racsbol_torles(self, kigyo: KigyoAdat) -> None:
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

    def _kigyok_racsozasa(self) -> None:
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

    def _pattogok_racsozasa(self) -> None:
        self.racs_vilag_patog.clear()
        for pattogo in self.patog_ellenseg:
            kulcs = KorSeged.kulcs(self.beallitasok.racsok_nagysaga, pattogo.x, pattogo.y)
            self.racs_vilag_patog[kulcs].append(pattogo.nev)

    def osszes_kigyo(self) -> List[KigyoAdat]:
        eredmeny = []
        for j in self.jatekosok.values():
            if isinstance(j, KigyoAdat):
                eredmeny.append(j)
        eredmeny.extend(self.kigyo_ellenseg)
        return eredmeny

    def _alma_mod_frissites(self, delta_ido) -> None:
        if not self.jatekosok and not self.kigyo_ellenseg:
            return
        
        for kigyo in self.osszes_kigyo():
            if not kigyo.el:
                continue
            if kigyo.jatekos_e:
                kigyo.sebesseg += (kigyo.cel_sebesseg - kigyo.sebesseg) * 0.18
            else:
                cel_dx, cel_dy = self._legjobb_irany_ai(kigyo, delta_ido)
                uj_dx, uj_dy = self._forditas_korlatozva(
                    kigyo.irany_x,
                    kigyo.irany_y,
                    cel_dx,
                    cel_dy
                )
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
          
    def kigyo_to_almak(self, kigyok: list):
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
          
    def _kigyo_fej_leptetes(self, kigyo: KigyoAdat, delta_ido) -> None:
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

    def _kigyo_etetes(self, kigyo: KigyoAdat) -> None:
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

    def _kigyo_utkozesek(self, kigyo: KigyoAdat) -> None:
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
                if idegen_id == kigyo.azonosito: # and pont_index < self.beallitasok.kigyo_onvedo_index:
                    continue
                if KorSeged.korok_utkozne_e(fej_x, fej_y, sugar, px, py, psugar * self.beallitasok.kigyo_utkozes_szorzo / 2):
                    kigyo.el = False
                    if idegen_id != kigyo.azonosito:
                        gyilkos = self._kigyo_keresese(idegen_id)
                        if gyilkos is not None:
                            gyilkos.olesek += 1
                    return

    def _kigyo_keresese(self, azonosito: str) -> Optional[KigyoAdat]:
        for kigyo in self.osszes_kigyo():
            if kigyo.azonosito == azonosito:
                return kigyo
        return None

    def _kozelebbi_almak(self, x: float, y: float) -> List[Tuple[float, float]]:
        eredmeny = []
        keresesi_tav = self.beallitasok.racsok_nagysaga * 2.2

        for kulcs in KorSeged.szomszed_kulcsok(
            self.beallitasok.racsok_nagysaga,
            x,
            y,
            keresesi_tav,
            2
        ):
            eredmeny.extend(self.racs_vilag_alma.get(kulcs, []))

        if not eredmeny:
            return []

        eredmeny.sort(key=lambda alma: KorSeged.tavolsag(x, y, alma[0], alma[1]))
        return eredmeny[:40]

    def _legjobb_irany_ai(self, kigyo: KigyoAdat, delta_ido) -> Tuple[float, float]:
        if self.frissitesi_szamlalo % kigyo.dontes_gyakorisag != kigyo.dontes_fazis:
            return kigyo.irany_x, kigyo.irany_y

        fej_x, fej_y = kigyo.fej_pozicio()

        almak = self._kozelebbi_almak(fej_x, fej_y)
        cel_x, cel_y = self._celpont_kereses(kigyo, almak)

        # Alapirány: alma felé
        alma_dx = cel_x - fej_x
        alma_dy = cel_y - fej_y
        alap_dx, alap_dy = KorSeged.normalizal(alma_dx, alma_dy)

        if abs(alap_dx) < 1e-6 and abs(alap_dy) < 1e-6:
            alap_dx, alap_dy = kigyo.irany_x, kigyo.irany_y

        veszely_tav = 50.0 + kigyo.sugar
        fal_puffer = kigyo.sugar + 10.0

        # 1) Falveszély vizsgálat
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

        # 2) Közeli kígyótest veszély
        for kulcs in KorSeged.szomszed_kulcsok(
            self.beallitasok.racsok_nagysaga,
            fej_x,
            fej_y,
            veszely_tav,
            1
        ):
            for idegen_id, pont_index, px, py, psugar in self.racs_vilag_kigyo.get(kulcs, []):
                if idegen_id == kigyo.azonosito:# and pont_index < self.beallitasok.kigyo_onvedo_index:
                    continue

                tav = KorSeged.tavolsag(fej_x, fej_y, px, py)
                hatar = veszely_tav + psugar

                if tav < hatar and tav > 1e-6:
                    veszely_van = True
                    menekulo_x += (fej_x - px) / tav
                    menekulo_y += (fej_y - py) / tav

        # 3) Ha van veszély, akkor menekülj
        if veszely_van:
            dx, dy = KorSeged.normalizal(menekulo_x, menekulo_y)

            if abs(dx) > 1e-6 or abs(dy) > 1e-6:
                return dx, dy

            # ha valamiért nem jött ki értelmes menekülő irány
            balra_dx, balra_dy = -kigyo.irany_y, kigyo.irany_x
            jobbra_dx, jobbra_dy = kigyo.irany_y, -kigyo.irany_x

            balra_bizt = self._irany_biztonsagos(kigyo, balra_dx, balra_dy, veszely_tav)
            jobbra_bizt = self._irany_biztonsagos(kigyo, jobbra_dx, jobbra_dy, veszely_tav)

            if balra_bizt and not jobbra_bizt:
                return KorSeged.normalizal(balra_dx, balra_dy)
            if jobbra_bizt and not balra_bizt:
                return KorSeged.normalizal(jobbra_dx, jobbra_dy)

            return KorSeged.normalizal(balra_dx, balra_dy)

        # 4) Ha nincs veszély, menjen az alma felé,
        # de csak ha az irány rövid távon biztonságos
        if self._irany_biztonsagos(kigyo, alap_dx, alap_dy, 38.0):
            return alap_dx, alap_dy

        # 5) Ha az alma iránya nem biztonságos, keress közeli alternatívát
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

    def _celpont_kereses(self, kigyo: KigyoAdat, almak: List[Tuple[float, float]]) -> Tuple[float, float]:
        fej_x, fej_y = kigyo.fej_pozicio()

        if almak:
            legjobb = None
            legjobb_tav = float("inf")

            for alma_x, alma_y in almak:
                tav = KorSeged.tavolsag(fej_x, fej_y, alma_x, alma_y)
                if tav < legjobb_tav:
                    legjobb_tav = tav
                    legjobb = (alma_x, alma_y)

            if legjobb is not None:
                return legjobb

        return (
            fej_x + kigyo.irany_x * 180.0,
            fej_y + kigyo.irany_y * 180.0,
        )

    def _irany_biztonsagos(self, kigyo: KigyoAdat, dx: float, dy: float, veszely_tav: float) -> bool:
        fej_x, fej_y = kigyo.fej_pozicio()

        for minta in (0.35, 0.7, 1.0):
            px = fej_x + dx * veszely_tav * minta
            py = fej_y + dy * veszely_tav * minta

            if (
                px < kigyo.sugar
                or px > self.beallitasok.vilag_szelesseg - kigyo.sugar
                or py < kigyo.sugar
                or py > self.beallitasok.vilag_magassag - kigyo.sugar
            ):
                return False

            for kulcs in KorSeged.szomszed_kulcsok(
                self.beallitasok.racsok_nagysaga,
                px,
                py,
                kigyo.sugar * 2.5,
                1
            ):
                for idegen_id, pont_index, resz_x, resz_y, resz_sugar in self.racs_vilag_kigyo.get(kulcs, []):
                    if idegen_id == kigyo.azonosito:# and pont_index < self.beallitasok.kigyo_onvedo_index:
                        continue

                    if KorSeged.korok_utkozne_e(px, py, kigyo.sugar, resz_x, resz_y, resz_sugar):
                        return False

        return True

    def _minta_veszely_pont(self, kigyo: KigyoAdat, px: float, py: float) -> float:
        buntetes = 0.0
        mintakulcsok = KorSeged.szomszed_kulcsok(self.beallitasok.racsok_nagysaga, px, py, kigyo.sugar * 3, 1)
        for kulcs in mintakulcsok:
            for idegen_id, pont_index, resz_x, resz_y, resz_sugar in self.racs_vilag_kigyo.get(kulcs, []):
                if idegen_id == kigyo.azonosito:# and pont_index < self.beallitasok.kigyo_onvedo_index:
                    continue
                tav = KorSeged.tavolsag(px, py, resz_x, resz_y)
                if tav < kigyo.sugar * 3.0:
                    buntetes += max(0.0, 5000.0 - tav * 150.0)
        return buntetes

    def _patogos_mod_frissites(self, delta_ido) -> None:
        if not self.jatekosok and not self.patog_ellenseg:
            return

        self._mozgas_pattogos_jatekosok(delta_ido)
        self._mozgas_pattogo_ellensegek(delta_ido)
        self._pattogok_potlas(max(0, self.max_patogok - len(self.patog_ellenseg)))
        self._pattogok_racsozasa()

    def _mozgas_pattogos_jatekosok(self, delta_ido) -> None:
        for jatekos in self.jatekosok.values():
            if not isinstance(jatekos, PattogoJatekos):
                continue
            if not jatekos.el:
                continue
            dx = (-1 if jatekos.mozog_balra else 0) + (1 if jatekos.mozog_jobbra else 0)
            dy = (-1 if jatekos.mozog_fel else 0) + (1 if jatekos.mozog_le else 0)
            ndx, ndy = KorSeged.normalizal(dx, dy)
            uj_x = jatekos.x + ndx * jatekos.sebesseg * delta_ido
            uj_y = jatekos.y + ndy * jatekos.sebesseg * delta_ido
            uj_x = max(jatekos.sugar, min(self.beallitasok.vilag_szelesseg - jatekos.sugar, uj_x))
            uj_y = max(jatekos.sugar, min(self.beallitasok.vilag_magassag - jatekos.sugar, uj_y))

            utkozik = False
            for masik in self.jatekosok.values():
                if not isinstance(masik, PattogoJatekos):
                    continue
                if masik.azonosito == jatekos.azonosito or not masik.el:
                    continue
                if KorSeged.korok_utkozne_e(uj_x, uj_y, jatekos.sugar, masik.x, masik.y, masik.sugar):
                    utkozik = True
                    break
            if not utkozik:
                for pattogo in self.patog_ellenseg:
                    if KorSeged.korok_utkozne_e(uj_x, uj_y, jatekos.sugar, pattogo.x, pattogo.y, pattogo.sugar):
                        utkozik = True
                        break
            if not utkozik:
                jatekos.x = uj_x
                jatekos.y = uj_y

    def _mozgas_pattogo_ellensegek(self, delta_ido) -> None:
        for pattogo in self.patog_ellenseg:
            pattogo.x += pattogo.dx * delta_ido
            pattogo.y += pattogo.dy * delta_ido

            if pattogo.x - pattogo.sugar < 0:
                pattogo.x = pattogo.sugar
                pattogo.dx = abs(pattogo.dx)
            elif pattogo.x + pattogo.sugar > self.beallitasok.vilag_szelesseg:
                pattogo.x = self.beallitasok.vilag_szelesseg - pattogo.sugar
                pattogo.dx = -abs(pattogo.dx)

            if pattogo.y - pattogo.sugar < 0:
                pattogo.y = pattogo.sugar
                pattogo.dy = abs(pattogo.dy)
            elif pattogo.y + pattogo.sugar > self.beallitasok.vilag_magassag:
                pattogo.y = self.beallitasok.vilag_magassag - pattogo.sugar
                pattogo.dy = -abs(pattogo.dy)

        for index in range(len(self.patog_ellenseg)):
            elso = self.patog_ellenseg[index]
            for masodik in self.patog_ellenseg[index + 1:]:
                if KorSeged.korok_utkozne_e(elso.x, elso.y, elso.sugar, masodik.x, masodik.y, masodik.sugar):
                    elso.dx, masodik.dx = -elso.dx, -masodik.dx
                    elso.dy, masodik.dy = -elso.dy, -masodik.dy

        for jatekos in self.jatekosok.values():
            if not isinstance(jatekos, PattogoJatekos) or not jatekos.el:
                continue
            for pattogo in self.patog_ellenseg:
                if KorSeged.korok_utkozne_e(jatekos.x, jatekos.y, jatekos.sugar, pattogo.x, pattogo.y, pattogo.sugar):
                    jatekos.hp -= 1
                    if jatekos.hp <= 0:
                        jatekos.el = False
                    tav = max(1.0, KorSeged.tavolsag(jatekos.x, jatekos.y, pattogo.x, pattogo.y))
                    nx = (jatekos.x - pattogo.x) / tav
                    ny = (jatekos.y - pattogo.y) / tav
                    jatekos.x = max(jatekos.sugar, min(self.beallitasok.vilag_szelesseg - jatekos.sugar, jatekos.x + nx * (jatekos.sugar + pattogo.sugar)))
                    jatekos.y = max(jatekos.sugar, min(self.beallitasok.vilag_magassag - jatekos.sugar, jatekos.y + ny * (jatekos.sugar + pattogo.sugar)))
                    pattogo.dx *= -1
                    pattogo.dy *= -1
                    break

    def kamera_pozicio(self, azonosito: str, szelesseg: int, magassag: int) -> Tuple[float, float]:
        if azonosito not in self.jatekosok:
            return 0.0, 0.0
        jatekos = self.jatekosok[azonosito]
        if self.jatek_mode == "alma":
            px, py = jatekos.fej_pozicio()
        else:
            px, py = jatekos.x, jatekos.y
        return px - szelesseg / 2, py - magassag / 2

    def nezet_jatekosnak(self, azonosito: str, szelesseg: int, magassag: int) -> dict:
        kamera_x, kamera_y = self.kamera_pozicio(azonosito, szelesseg, magassag)

        
            

        allapot = {
            "jatek_mode": self.jatek_mode,
            "nehezseg_szint": self.nehezseg_szint,
            "vilag_szelesseg": self.beallitasok.vilag_szelesseg,
            "vilag_magassag": self.beallitasok.vilag_magassag,
            "kamera_x": kamera_x,
            "kamera_y": kamera_y,
            "sajat_id": azonosito,
        }
        top = sorted(self.osszes_kigyo(), key=lambda k: k.alma_pontok, reverse=True)[:self.beallitasok.top_hany]

        szoveg = []
        for kigyo in top:
            nev = kigyo.nev
            testhossz = len(kigyo.test_pontok)
            oles = kigyo.olesek
            pontszam = kigyo.alma_pontok

            szoveg.append((nev, testhossz, oles, pontszam))
        allapot["toplista"] = szoveg
        if self.jatek_mode == "alma":
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
        
        else:
            allapot["jatekosok"] = {
                az: jatekos.allapot_dict()
                for az, jatekos in self.jatekosok.items()
            }
            allapot["patog_ellenseg"] = [
                pattogo.allapot_dict() for pattogo in self._lathato_pattogok(kamera_x, kamera_y, szelesseg, magassag)
            ]
        return allapot

    def lathato_kigyo_azonositok(self, kamera_x: float, kamera_y: float, szelesseg: int, magassag: int, sajat_id: Optional[str] = None) -> set[str]:
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
        
    def _lathato_almak(self, kamera_x: float, kamera_y: float, szelesseg: int, magassag: int) -> List[Tuple[float, float]]:
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

    def _lathato_pattogok(self, kamera_x: float, kamera_y: float, szelesseg: int, magassag: int) -> List[PattogoEllenseg]:
        bal = kamera_x - self.beallitasok.patogo_rajzolas_puffer
        jobb = kamera_x + szelesseg + self.beallitasok.patogo_rajzolas_puffer
        fent = kamera_y - self.beallitasok.patogo_rajzolas_puffer
        lent = kamera_y + magassag + self.beallitasok.patogo_rajzolas_puffer
        eredmeny = []
        for pattogo in self.patog_ellenseg:
            if bal < pattogo.x < jobb and fent < pattogo.y < lent:
                eredmeny.append(pattogo)
        return eredmeny

    def _forditas_korlatozva(self, aktualis_dx: float, aktualis_dy: float, cel_dx: float, cel_dy: float) -> Tuple[float, float]:
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

def kodbol_port(kod: str, beallitasok: Optional[Beallitasok] = None) -> int:
    b = beallitasok or Beallitasok()
    szam = int(kod)
    return b.szerver_alap_port + (szam % b.szerver_port_tartomany)
