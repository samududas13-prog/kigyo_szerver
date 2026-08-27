import json, os

def ldtk_terkep_betoltes(fajl, szoba_nev=None):
    with open(fajl, "r", encoding="utf-8") as f:
        adat = json.load(f)

    RETEG_BEALLITASOK = {
        "Bg_textures": {
            "szerep": "hatter",
            "intgrid": {},
        },

        "Wall_shadows": {
            "szerep": "eloter",
            "intgrid": {},
        },

        "Collisions": {
            "szerep": "platform",
            "intgrid": {
                1: {
                    "fajta": "dirt",
                    "utkozik": True,
                },

                2: {
                    "fajta": "ladder",
                    "utkozik": False,
                },

                3: {
                    "fajta": "stone",
                    "utkozik": True,
                },
            },
        },

        "Block": {
            "szerep": "platform",
            "intgrid": {
                1: {
                    "fajta": "ice",
                    "utkozik": True,
                },

                2: {
                    "fajta": "gomba",
                    "utkozik": False,
                },
            },
        },

        "Lava": {
            "szerep": "veszely",
            "intgrid": {
                1: {
                    "fajta": "lava",
                    "utkozik": False,
                    "sebez": True,
                },
            },
        },

        "Erdos": {
            "szerep": "kihagy",
            "intgrid": {},
        },

        "Entities": {
            "szerep": "kihagy",
            "intgrid": {},
        },
    }

    szobak = {}

    for vilag in adat.get("worlds", []):
        for szoba in vilag.get("levels", []):
            szobak[szoba["identifier"]] = szoba

    if not szobak:
        for szoba in adat.get("levels", []):
            szobak[szoba["identifier"]] = szoba

    if not szobak:
        raise ValueError("Az LDtk fájlban nincs egyetlen szoba sem.")

    if szoba_nev is not None and szoba_nev in szobak:
        szoba = szobak[szoba_nev]
    else:
        szoba = next(iter(szobak.values()))

    rajz_retegek = {
        "hatter": {},
        "platform": {},
        "veszely": {},
        "eloter": {},
    }

    platformok = {}
    platform_racs = {}

    veszelyek = {}
    veszely_racs = {}

    kulonleges_racs = {}

    platform_sorszam = 0
    veszely_sorszam = 0

    platform_racs_meret = 16

    retegek = szoba.get("layerInstances") or []

    # ----------------------------------------------------------
    # 1. RAJZOLÁSI ADATOK
    #
    # autoLayerTiles és gridTiles CSAK rajzolásra szolgálnak.
    # Innen SOHA nem készül collision.
    # ----------------------------------------------------------

    for reteg in reversed(retegek):
        reteg_nev = reteg["__identifier"]

        reteg_beallitas = RETEG_BEALLITASOK.get(
            reteg_nev,
            {
                "szerep": "kihagy",
                "intgrid": {},
            }
        )

        szerep = reteg_beallitas["szerep"]

        if szerep == "kihagy":
            continue

        tileset_ut = reteg.get("__tilesetRelPath")

        if tileset_ut:
            kep_fajl = os.path.basename(tileset_ut.replace("\\", "/"))
        else:
            kep_fajl = None

        csempe_meret = reteg["__gridSize"]

        eltol_x = reteg.get("__pxTotalOffsetX", 0)
        eltol_y = reteg.get("__pxTotalOffsetY", 0)

        csempek = {}
        csempe_sorszam = 0

        osszes_csempe = reteg.get("autoLayerTiles", []) + reteg.get("gridTiles", [])

        for csempe in osszes_csempe:
            x = (csempe["px"][0] + eltol_x)
            y = (csempe["px"][1] + eltol_y)

            csempek[csempe_sorszam] = {
                "x": x,
                "y": y,

                "forras_x": csempe["src"][0],
                "forras_y": csempe["src"][1],

                "csempe_id": csempe["t"],

                "tukrozes": csempe["f"],
                "atlatszosag": csempe["a"],
            }

            csempe_sorszam += 1

        if kep_fajl is not None:
            rajz_retegek[szerep][reteg_nev] = {
                "nev": reteg_nev,
                "szerep": szerep,

                "kep_fajl": kep_fajl,

                "csempe_meret": csempe_meret,

                "atlatszosag": reteg.get("__opacity", 1.0),

                "csempek": csempek,
            }

    # ----------------------------------------------------------
    # 2. FIZIKA
    #
    # Collision KIZÁRÓLAG az IntGridből készül.
    # ----------------------------------------------------------

    for reteg in retegek:
        reteg_nev = reteg["__identifier"]

        reteg_beallitas = RETEG_BEALLITASOK.get(
            reteg_nev,
            {
                "szerep": "kihagy",
                "intgrid": {},
            }
        )

        intgrid_beallitasok = reteg_beallitas.get("intgrid", {})

        if not intgrid_beallitasok:
            continue

        int_grid = reteg.get("intGridCsv", [])

        if not int_grid:
            continue

        csempe_meret = reteg["__gridSize"]
        racs_szelesseg = reteg["__cWid"]

        eltol_x = reteg.get("__pxTotalOffsetX", 0)
        eltol_y = reteg.get("__pxTotalOffsetY", 0)

        for sorszam, ertek in enumerate(int_grid):
            if ertek == 0:
                continue

            ertek_beallitas = intgrid_beallitasok.get(ertek)

            if ertek_beallitas is None:
                continue

            helyi_cella_x = sorszam % racs_szelesseg
            helyi_cella_y = sorszam // racs_szelesseg

            x = (helyi_cella_x * csempe_meret + eltol_x)
            y = (helyi_cella_y * csempe_meret + eltol_y)

            cella_x = int(x // csempe_meret)
            cella_y = int(y // csempe_meret)

            fajta = ertek_beallitas.get("fajta", "alap")
            utkozik = ertek_beallitas.get("utkozik", False)
            sebez = ertek_beallitas.get("sebez", False)

            fizikai_adat = {
                "x": x,
                "y": y,

                "width": csempe_meret,
                "height": csempe_meret,

                "reteg": reteg_nev,

                "fajta": fajta,

                "intgrid_ertek": ertek,

                "utkozik": utkozik,
                "sebez": sebez,
            }

            # ----------------------------------------------
            # Normál szilárd platform
            # ----------------------------------------------

            if utkozik:
                platformok[platform_sorszam] = fizikai_adat
                platform_racs[(cella_x, cella_y)] = fizikai_adat

                platform_sorszam += 1
                platform_racs_meret = csempe_meret

            # ----------------------------------------------
            # Sebző terület, például láva
            # ----------------------------------------------

            if sebez:
                veszelyek[veszely_sorszam] = fizikai_adat
                veszely_racs[(cella_x, cella_y)] = fizikai_adat

                veszely_sorszam += 1

            # ----------------------------------------------
            # Nem ütköző különleges dolgok:
            # gomba, létra stb.
            # ----------------------------------------------

            if not utkozik and not sebez:
                kulonleges_racs[(cella_x, cella_y)] = fizikai_adat

    return {
        "szoba": szoba["identifier"],

        "width": szoba["pxWid"],
        "height": szoba["pxHei"],

        "hatter_szin": szoba.get("__bgColor", "#000000"),

        # Fizikai platformok
        "platformok": platformok,
        "platform_racs": platform_racs,
        "platform_racs_meret": platform_racs_meret,

        # Láva és későbbi veszélyek
        "veszelyek": veszelyek,
        "veszely_racs": veszely_racs,

        # Gomba, létra stb.
        "kulonleges_racs": kulonleges_racs,

        # Rajzolási adatok
        "rajz_retegek": rajz_retegek,

        # Régi kód kompatibilitása miatt
        "ground": {},
        "portok": {},
    }