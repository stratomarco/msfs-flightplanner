# ============================================================
# MSFS 2024 Aircraft Profiles
# Default MSFS 2024 aircraft + confirmed 3rd party releases
# as of February 2026
# ============================================================

AIRCRAFT_PROFILES = {

    # ── GA SINGLE ENGINE PISTON ──────────────────────────────
    "1": {
        "label":         "Cessna 152",
        "developer":     "Asobo (Default)",
        "simbrief_code": "C152",
        "cruise_kts":    90,
        "cruise_alt":    6500,
        "min_runway_ft": 1500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     600,
        "descent_fpm":   400,
    },
    "2": {
        "label":         "Cessna 172 Skyhawk",
        "developer":     "Asobo (Default)",
        "simbrief_code": "C172",
        "cruise_kts":    110,
        "cruise_alt":    7500,
        "min_runway_ft": 1800,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     700,
        "descent_fpm":   500,
    },
    "3": {
        "label":         "Cessna 182 Skylane",
        "developer":     "Asobo (Default)",
        "simbrief_code": "C182",
        "cruise_kts":    130,
        "cruise_alt":    8500,
        "min_runway_ft": 1800,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     850,
        "descent_fpm":   600,
    },
    "4": {
        "label":         "Cessna 400 Corvalis TT",
        "developer":     "Carenado (Default)",
        "simbrief_code": "P210",
        "cruise_kts":    185,
        "cruise_alt":    12000,
        "min_runway_ft": 2200,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     1200,
        "descent_fpm":   800,
    },
    "5": {
        "label":         "Cirrus SR22",
        "developer":     "Asobo (Default)",
        "simbrief_code": "SR22",
        "cruise_kts":    175,
        "cruise_alt":    10500,
        "min_runway_ft": 2000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     1100,
        "descent_fpm":   700,
    },
    "6": {
        "label":         "Beechcraft Bonanza G36",
        "developer":     "Asobo (Default)",
        "simbrief_code": "BE36",
        "cruise_kts":    165,
        "cruise_alt":    9500,
        "min_runway_ft": 2000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     1000,
        "descent_fpm":   650,
    },
    "7": {
        "label":         "Piper PA-18 Super Cub",
        "developer":     "Asobo (Default)",
        "simbrief_code": "PA18",
        "cruise_kts":    85,
        "cruise_alt":    6000,
        "min_runway_ft": 500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     700,
        "descent_fpm":   400,
    },

    # ── GA SINGLE — JUST FLIGHT ──────────────────────────────
    "8": {
        "label":         "Piper PA-28-161 Warrior II",
        "developer":     "Just Flight (3rd Party)",
        "simbrief_code": "PA28",
        "cruise_kts":    110,
        "cruise_alt":    7500,
        "min_runway_ft": 1800,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     650,
        "descent_fpm":   450,
    },
    "9": {
        "label":         "Piper PA-28R Arrow III",
        "developer":     "Just Flight (3rd Party)",
        "simbrief_code": "PA28",
        "cruise_kts":    140,
        "cruise_alt":    9000,
        "min_runway_ft": 2000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     800,
        "descent_fpm":   550,
    },
    "10": {
        "label":         "Piper PA-28R Turbo Arrow III/IV",
        "developer":     "Just Flight (3rd Party)",
        "simbrief_code": "PA28",
        "cruise_kts":    160,
        "cruise_alt":    12000,
        "min_runway_ft": 2000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     950,
        "descent_fpm":   650,
    },

    # ── GA SINGLE — A2A SIMULATIONS ─────────────────────────
    "11": {
        "label":         "Piper Comanche 250 (Accu-Sim)",
        "developer":     "A2A Simulations (3rd Party)",
        "simbrief_code": "PA24",
        "cruise_kts":    160,
        "cruise_alt":    10000,
        "min_runway_ft": 2000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     1000,
        "descent_fpm":   650,
    },
    "12": {
        "label":         "Aerostar 600 (Accu-Sim)",
        "developer":     "A2A Simulations (3rd Party)",
        "simbrief_code": "AEST",
        "cruise_kts":    220,
        "cruise_alt":    20000,
        "min_runway_ft": 2500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_TWIN",
        "climb_fpm":     1500,
        "descent_fpm":   1000,
    },

    # ── GA TWIN PISTON ───────────────────────────────────────
    "13": {
        "label":         "Beechcraft Baron G58",
        "developer":     "Asobo (Default)",
        "simbrief_code": "BE58",
        "cruise_kts":    190,
        "cruise_alt":    10000,
        "min_runway_ft": 2200,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_TWIN",
        "climb_fpm":     1200,
        "descent_fpm":   800,
    },
    "14": {
        "label":         "Baron Professional (Black Square)",
        "developer":     "Black Square / Just Flight (3rd Party)",
        "simbrief_code": "BE58",
        "cruise_kts":    195,
        "cruise_alt":    12000,
        "min_runway_ft": 2200,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_TWIN",
        "climb_fpm":     1300,
        "descent_fpm":   900,
    },
    "15": {
        "label":         "Bonanza Professional (Black Square)",
        "developer":     "Black Square / Just Flight (3rd Party)",
        "simbrief_code": "BE36",
        "cruise_kts":    170,
        "cruise_alt":    10000,
        "min_runway_ft": 2000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_PISTON",
        "climb_fpm":     1050,
        "descent_fpm":   700,
    },
    "16": {
        "label":         "Piston Duke (Black Square)",
        "developer":     "Black Square / Just Flight (3rd Party)",
        "simbrief_code": "BE60",
        "cruise_kts":    220,
        "cruise_alt":    25000,
        "min_runway_ft": 3000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "GA_TWIN",
        "climb_fpm":     1500,
        "descent_fpm":   1100,
    },

    # ── TURBOPROPS ───────────────────────────────────────────
    "17": {
        "label":         "Daher TBM 930",
        "developer":     "Asobo (Default)",
        "simbrief_code": "TBM9",
        "cruise_kts":    300,
        "cruise_alt":    28000,
        "min_runway_ft": 2800,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     2000,
        "descent_fpm":   1500,
    },
    "18": {
        "label":         "TBM 850 (Black Square)",
        "developer":     "Black Square / Just Flight (3rd Party)",
        "simbrief_code": "TBM8",
        "cruise_kts":    290,
        "cruise_alt":    31000,
        "min_runway_ft": 2800,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1900,
        "descent_fpm":   1500,
    },
    "19": {
        "label":         "Turbine Duke (Black Square)",
        "developer":     "Black Square / Just Flight (3rd Party)",
        "simbrief_code": "BE60",
        "cruise_kts":    285,
        "cruise_alt":    31000,
        "min_runway_ft": 3000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1700,
        "descent_fpm":   1400,
    },
    "20": {
        "label":         "Pilatus PC-12 NGX",
        "developer":     "SimWorks Studios (Default)",
        "simbrief_code": "PC12",
        "cruise_kts":    270,
        "cruise_alt":    25000,
        "min_runway_ft": 2500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1800,
        "descent_fpm":   1400,
    },
    "21": {
        "label":         "Cessna Caravan Professional (Black Square)",
        "developer":     "Black Square / Just Flight (3rd Party)",
        "simbrief_code": "C208",
        "cruise_kts":    175,
        "cruise_alt":    12000,
        "min_runway_ft": 1500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1100,
        "descent_fpm":   900,
    },
    "22": {
        "label":         "DHC-6 Twin Otter",
        "developer":     "Asobo (Default)",
        "simbrief_code": "DHC6",
        "cruise_kts":    170,
        "cruise_alt":    10000,
        "min_runway_ft": 1000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1200,
        "descent_fpm":   900,
    },
    "23": {
        "label":         "Beechcraft King Air C90 GTX",
        "developer":     "Blackbird Sims (Default)",
        "simbrief_code": "BE9L",
        "cruise_kts":    240,
        "cruise_alt":    22000,
        "min_runway_ft": 3000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1800,
        "descent_fpm":   1400,
    },
    "24": {
        "label":         "ATR 72-600",
        "developer":     "Asobo (Default)",
        "simbrief_code": "AT76",
        "cruise_kts":    270,
        "cruise_alt":    25000,
        "min_runway_ft": 4000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1600,
        "descent_fpm":   1400,
    },
    "25": {
        "label":         "Cessna 408 SkyCourier",
        "developer":     "Asobo (Default — Deluxe)",
        "simbrief_code": "C408",
        "cruise_kts":    200,
        "cruise_alt":    15000,
        "min_runway_ft": 2500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "TURBO",
        "climb_fpm":     1400,
        "descent_fpm":   1000,
    },

    # ── BUSINESS JETS ────────────────────────────────────────
    "26": {
        "label":         "Cirrus Vision SF50",
        "developer":     "FlightFX (Default)",
        "simbrief_code": "SF50",
        "cruise_kts":    300,
        "cruise_alt":    28000,
        "min_runway_ft": 3000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     2000,
        "descent_fpm":   1800,
    },
    "27": {
        "label":         "Cessna Citation CJ4",
        "developer":     "Working Title (Default)",
        "simbrief_code": "C25C",
        "cruise_kts":    390,
        "cruise_alt":    45000,
        "min_runway_ft": 3500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     2800,
        "descent_fpm":   2200,
    },
    "28": {
        "label":         "Pilatus PC-24",
        "developer":     "Asobo (Default — Premium Deluxe)",
        "simbrief_code": "PC24",
        "cruise_kts":    430,
        "cruise_alt":    45000,
        "min_runway_ft": 2900,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     3000,
        "descent_fpm":   2500,
    },
    "29": {
        "label":         "HondaJet Elite II",
        "developer":     "FlightFX (Default)",
        "simbrief_code": "HN700",
        "cruise_kts":    420,
        "cruise_alt":    43000,
        "min_runway_ft": 4000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     2800,
        "descent_fpm":   2200,
    },
    "30": {
        "label":         "BAe 146 Professional",
        "developer":     "Just Flight (3rd Party)",
        "simbrief_code": "B461",
        "cruise_kts":    400,
        "cruise_alt":    35000,
        "min_runway_ft": 4500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     2200,
        "descent_fpm":   1800,
    },
    "31": {
        "label":         "Avro RJ Professional",
        "developer":     "Just Flight (3rd Party)",
        "simbrief_code": "RJ1H",
        "cruise_kts":    400,
        "cruise_alt":    35000,
        "min_runway_ft": 4500,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     2200,
        "descent_fpm":   1800,
    },
    "32": {
        "label":         "Fokker F28 Professional",
        "developer":     "Just Flight (3rd Party)",
        "simbrief_code": "F28",
        "cruise_kts":    420,
        "cruise_alt":    35000,
        "min_runway_ft": 5000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "BIZ_JET",
        "climb_fpm":     2400,
        "descent_fpm":   2000,
    },

    # ── REGIONAL ─────────────────────────────────────────────
    "33": {
        "label":         "Airbus A220-300",
        "developer":     "Asobo (Default)",
        "simbrief_code": "BCS3",
        "cruise_kts":    450,
        "cruise_alt":    41000,
        "min_runway_ft": 5500,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "REGIONAL",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "34": {
        "label":         "Embraer E175",
        "developer":     "Asobo (Default)",
        "simbrief_code": "E170",
        "cruise_kts":    420,
        "cruise_alt":    41000,
        "min_runway_ft": 5000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "REGIONAL",
        "climb_fpm":     2400,
        "descent_fpm":   2000,
    },
    "35": {
        "label":         "Saab 340B",
        "developer":     "Asobo (Default)",
        "simbrief_code": "SF34",
        "cruise_kts":    250,
        "cruise_alt":    25000,
        "min_runway_ft": 4000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "REGIONAL",
        "climb_fpm":     1600,
        "descent_fpm":   1400,
    },

    # ── NARROWBODY AIRLINERS ─────────────────────────────────
    "36": {
        "label":         "Boeing 737 MAX 8 (Default)",
        "developer":     "Asobo (Default)",
        "simbrief_code": "B38M",
        "cruise_kts":    450,
        "cruise_alt":    41000,
        "min_runway_ft": 6000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2800,
        "descent_fpm":   2200,
    },
    "37": {
        "label":         "Boeing 737-600 (PMDG)",
        "developer":     "PMDG (3rd Party)",
        "simbrief_code": "B736",
        "cruise_kts":    448,
        "cruise_alt":    41000,
        "min_runway_ft": 5500,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2800,
        "descent_fpm":   2200,
    },
    "38": {
        "label":         "Boeing 737-800 (PMDG)",
        "developer":     "PMDG (3rd Party)",
        "simbrief_code": "B738",
        "cruise_kts":    450,
        "cruise_alt":    41000,
        "min_runway_ft": 6000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2800,
        "descent_fpm":   2200,
    },
    "39": {
        "label":         "Boeing 737-900 (PMDG)",
        "developer":     "PMDG (3rd Party)",
        "simbrief_code": "B739",
        "cruise_kts":    450,
        "cruise_alt":    41000,
        "min_runway_ft": 6500,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2800,
        "descent_fpm":   2200,
    },
    "40": {
        "label":         "Airbus A320neo (Default)",
        "developer":     "Asobo (Default)",
        "simbrief_code": "A20N",
        "cruise_kts":    450,
        "cruise_alt":    39000,
        "min_runway_ft": 6000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "41": {
        "label":         "Airbus A320ceo (Fenix)",
        "developer":     "Fenix Simulations (3rd Party)",
        "simbrief_code": "A320",
        "cruise_kts":    450,
        "cruise_alt":    39000,
        "min_runway_ft": 6000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "42": {
        "label":         "Airbus A319ceo (Fenix)",
        "developer":     "Fenix Simulations (3rd Party)",
        "simbrief_code": "A319",
        "cruise_kts":    448,
        "cruise_alt":    39000,
        "min_runway_ft": 5500,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "43": {
        "label":         "Airbus A321LR (Default)",
        "developer":     "Asobo (Default)",
        "simbrief_code": "A21N",
        "cruise_kts":    450,
        "cruise_alt":    39000,
        "min_runway_ft": 7000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "44": {
        "label":         "Airbus A32NX (FlyByWire)",
        "developer":     "FlyByWire Simulations (Freeware)",
        "simbrief_code": "A20N",
        "cruise_kts":    450,
        "cruise_alt":    39000,
        "min_runway_ft": 6000,
        "type_filter":   ["medium_airport", "large_airport"],
        "category":      "NARROWBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },

    # ── WIDEBODY AIRLINERS ───────────────────────────────────
    "45": {
        "label":         "Boeing 787-10 Dreamliner",
        "developer":     "Asobo (Default)",
        "simbrief_code": "B78X",
        "cruise_kts":    490,
        "cruise_alt":    43000,
        "min_runway_ft": 8000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "46": {
        "label":         "Airbus A330-300",
        "developer":     "iniBuilds (Default)",
        "simbrief_code": "A333",
        "cruise_kts":    480,
        "cruise_alt":    41000,
        "min_runway_ft": 8000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2400,
        "descent_fpm":   2000,
    },
    "47": {
        "label":         "Boeing 777-200ER (PMDG)",
        "developer":     "PMDG (3rd Party)",
        "simbrief_code": "B772",
        "cruise_kts":    490,
        "cruise_alt":    43000,
        "min_runway_ft": 9000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "48": {
        "label":         "Boeing 777-300ER (PMDG)",
        "developer":     "PMDG (3rd Party)",
        "simbrief_code": "B77W",
        "cruise_kts":    490,
        "cruise_alt":    43000,
        "min_runway_ft": 10000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "49": {
        "label":         "Boeing 777F (PMDG)",
        "developer":     "PMDG (3rd Party)",
        "simbrief_code": "B77F",
        "cruise_kts":    490,
        "cruise_alt":    43000,
        "min_runway_ft": 10000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2500,
        "descent_fpm":   2000,
    },
    "50": {
        "label":         "Boeing 747-8 Intercontinental",
        "developer":     "Asobo (Default)",
        "simbrief_code": "B748",
        "cruise_kts":    490,
        "cruise_alt":    43000,
        "min_runway_ft": 10000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2200,
        "descent_fpm":   1800,
    },
    "51": {
        "label":         "Airbus A380X (FlyByWire)",
        "developer":     "FlyByWire Simulations (Freeware)",
        "simbrief_code": "A388",
        "cruise_kts":    490,
        "cruise_alt":    43000,
        "min_runway_ft": 10000,
        "type_filter":   ["large_airport"],
        "category":      "WIDEBODY",
        "climb_fpm":     2200,
        "descent_fpm":   1800,
    },

    # ── SPECIAL / MILITARY ───────────────────────────────────
    "52": {
        "label":         "Airbus A400M Atlas",
        "developer":     "iniBuilds (Default)",
        "simbrief_code": "A400",
        "cruise_kts":    390,
        "cruise_alt":    37000,
        "min_runway_ft": 3000,
        "type_filter":   ["small_airport", "medium_airport", "large_airport"],
        "category":      "MILITARY",
        "climb_fpm":     2000,
        "descent_fpm":   1800,
    },
}

# ── Category display order for the table ────────────────────
CATEGORY_ORDER = [
    "GA_PISTON", "GA_TWIN", "TURBO", "BIZ_JET",
    "REGIONAL", "NARROWBODY", "WIDEBODY", "MILITARY"
]

CATEGORY_LABELS = {
    "GA_PISTON":  "GA — Single Engine Piston",
    "GA_TWIN":    "GA — Twin Piston / Light Twin",
    "TURBO":      "Turboprop",
    "BIZ_JET":    "Business / Regional Jet",
    "REGIONAL":   "Regional Airliner",
    "NARROWBODY": "Narrowbody Airliner",
    "WIDEBODY":   "Widebody Airliner",
    "MILITARY":   "Military / Special",
}


def select_aircraft(console) -> dict:
    """Interactive aircraft selection with category grouping."""
    from rich.table import Table

    table = Table(
        title="[bold cyan]MSFS 2024 Aircraft — Select Your Type[/bold cyan]",
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column("#",          style="bold white", width=4)
    table.add_column("Aircraft",   style="cyan",       width=35)
    table.add_column("Developer",  style="dim white",  width=30)
    table.add_column("Cruise",     style="green",      width=10)
    table.add_column("Alt",        style="yellow",     width=10)
    table.add_column("Min RWY",    style="magenta",    width=10)

    current_category = None
    for key, ac in AIRCRAFT_PROFILES.items():
        cat = ac["category"]
        if cat != current_category:
            current_category = cat
            table.add_row(
                "", f"[bold yellow]── {CATEGORY_LABELS[cat]} ──[/bold yellow]",
                "", "", "", "",
            )
        table.add_row(
            key,
            ac["label"],
            ac["developer"],
            f"{ac['cruise_kts']} kt",
            f"{ac['cruise_alt']:,} ft",
            f"{ac['min_runway_ft']:,} ft",
        )

    console.print(table)

    while True:
        choice = console.input(
            "[bold yellow]Select aircraft number: [/bold yellow]"
        ).strip()
        if choice in AIRCRAFT_PROFILES:
            ac = AIRCRAFT_PROFILES[choice]
            console.print(
                f"\n[green]✓ Selected:[/green] [cyan]{ac['label']}[/cyan] "
                f"([dim]{ac['developer']}[/dim])\n"
            )
            return ac
        console.print(
            f"[red]Invalid. Enter a number between 1 and {len(AIRCRAFT_PROFILES)}.[/red]"
        )


def estimate_flight_time(dist_nm: float, aircraft: dict) -> str:
    """Estimate total block time including climb and descent. Returns '1h 23m'."""
    cruise_kts  = aircraft["cruise_kts"]
    cruise_alt  = aircraft["cruise_alt"]
    climb_fpm   = aircraft["climb_fpm"]
    descent_fpm = aircraft["descent_fpm"]

    climb_min   = cruise_alt / climb_fpm
    descent_min = cruise_alt / descent_fpm
    climb_nm    = (climb_min / 60)   * (cruise_kts * 0.6)
    descent_nm  = (descent_min / 60) * (cruise_kts * 0.7)
    cruise_nm   = max(0, dist_nm - climb_nm - descent_nm)
    cruise_min  = (cruise_nm / cruise_kts) * 60

    total_min = climb_min + cruise_min + descent_min
    hours = int(total_min // 60)
    mins  = int(total_min % 60)
    return f"{hours}h {mins:02d}m" if hours > 0 else f"{mins}m"


def nm_range_for_hours(hours: float, aircraft: dict) -> tuple:
    """Return (min_nm, max_nm) for a target duration with ±15% tolerance."""
    target_nm = aircraft["cruise_kts"] * hours
    return target_nm * 0.85, target_nm * 1.15