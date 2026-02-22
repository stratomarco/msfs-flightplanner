# ============================================================
# POH Performance Data — keyed by simbrief_code from aircraft.py
# Sources documented per entry. Tier 1 = direct POH/AFM data.
# Tier 2 = manufacturer published specs / authoritative reviews.
# Tier 3 = best available approximation, flagged clearly.
# ============================================================
#
# cruise_table rows: { fl, ktas, fuel_gph OR fuel_pph, power_pct, notes }
# fuel_unit: "gal" for piston/turboprop in GPH, "lbs" for jets in PPH
# All fuel quantities in the matching unit (gal or lbs)

POH = {

    # ════════════════════════════════════════════════════════
    # GA SINGLE ENGINE PISTON
    # ════════════════════════════════════════════════════════

    "C152": {
        "label":          "Cessna 152",
        "fuel_type":      "AvGas",
        "fuel_capacity":  24.5,        # usable gallons
        "fuel_unit":      "gal",
        "taxi_fuel":      1.0,
        "reserve_fuel":   3.8,         # 45 min @ 5 gph
        "climb":          {"fpm": 715, "ktas": 67, "fuel_gph": 6.5},
        "cruise_table": [
            {"fl":  20, "ktas":  90, "fuel_gph": 5.5, "power_pct": 75, "notes": "2000ft 75%"},
            {"fl":  45, "ktas":  92, "fuel_gph": 5.3, "power_pct": 75, "notes": "4500ft 75%"},
            {"fl":  65, "ktas":  93, "fuel_gph": 5.0, "power_pct": 70, "notes": "6500ft 70%"},
            {"fl":  85, "ktas":  91, "fuel_gph": 4.7, "power_pct": 65, "notes": "8500ft LRC"},
        ],
        "descent":        {"fpm": 500, "ktas": 85, "fuel_gph": 3.5},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Cessna 152 POH Section 5",
    },

    "C172": {
        "label":          "Cessna 172S Skyhawk",
        "fuel_type":      "AvGas",
        "fuel_capacity":  53.0,        # 56 total, 53 usable
        "fuel_unit":      "gal",
        "taxi_fuel":      1.4,         # POH Note 1
        "reserve_fuel":   5.5,         # 45 min @ 7.3 gph
        "climb":          {"fpm": 730, "ktas": 76, "fuel_gph": 10.0},
        "cruise_table": [
            {"fl":  25, "ktas": 107, "fuel_gph": 8.4, "power_pct": 75, "notes": "2500ft 75% std day"},
            {"fl":  45, "ktas": 110, "fuel_gph": 8.4, "power_pct": 75, "notes": "4500ft 75%"},
            {"fl":  65, "ktas": 112, "fuel_gph": 8.2, "power_pct": 75, "notes": "6500ft 75%"},
            {"fl":  85, "ktas": 114, "fuel_gph": 8.0, "power_pct": 75, "notes": "8500ft best cruise"},
            {"fl": 105, "ktas": 115, "fuel_gph": 7.5, "power_pct": 65, "notes": "10500ft 65%"},
            {"fl": 125, "ktas": 111, "fuel_gph": 6.9, "power_pct": 55, "notes": "12500ft LRC"},
        ],
        "descent":        {"fpm": 500, "ktas": 110, "fuel_gph": 5.5},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Cessna 172S POH P/N 172SPHBUS-00 Section 5",
    },

    "C182": {
        "label":          "Cessna 182T Skylane",
        "fuel_type":      "AvGas",
        "fuel_capacity":  87.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      1.5,
        "reserve_fuel":   7.5,
        "climb":          {"fpm": 924, "ktas": 84, "fuel_gph": 14.0},
        "cruise_table": [
            {"fl":  40, "ktas": 140, "fuel_gph": 13.2, "power_pct": 75, "notes": "4000ft 75%"},
            {"fl":  65, "ktas": 143, "fuel_gph": 12.8, "power_pct": 75, "notes": "6500ft 75%"},
            {"fl":  85, "ktas": 144, "fuel_gph": 12.5, "power_pct": 75, "notes": "8500ft best cruise"},
            {"fl": 105, "ktas": 142, "fuel_gph": 11.5, "power_pct": 68, "notes": "10500ft 68%"},
            {"fl": 125, "ktas": 137, "fuel_gph": 10.0, "power_pct": 60, "notes": "12500ft LRC"},
        ],
        "descent":        {"fpm": 600, "ktas": 130, "fuel_gph": 7.0},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Cessna 182T POH Section 5",
    },

    # Cessna 400 Corvalis TT — turbocharged 310hp Continental TSIO-550-C
    "P210": {
        "label":          "Cessna 400 Corvalis TT",
        "fuel_type":      "AvGas",
        "fuel_capacity":  102.0,       # 102 usable gallons
        "fuel_unit":      "gal",
        "taxi_fuel":      1.5,
        "reserve_fuel":   11.5,        # 45 min @ 15.3 gph
        "climb":          {"fpm": 1400, "ktas": 110, "fuel_gph": 20.0},
        "cruise_table": [
            {"fl":  80, "ktas": 183, "fuel_gph": 17.0, "power_pct": 85, "notes": "8000ft 85% max cruise"},
            {"fl": 100, "ktas": 191, "fuel_gph": 16.5, "power_pct": 85, "notes": "10000ft 85%"},
            {"fl": 140, "ktas": 200, "fuel_gph": 15.5, "power_pct": 80, "notes": "14000ft 80% — published max 235 KTAS"},
            {"fl": 170, "ktas": 195, "fuel_gph": 13.5, "power_pct": 75, "notes": "17000ft 75%"},
            {"fl": 200, "ktas": 185, "fuel_gph": 11.5, "power_pct": 65, "notes": "20000ft LRC"},
        ],
        "descent":        {"fpm": 800, "ktas": 160, "fuel_gph": 8.0},
        "contingency_pct": 10,
        "tier": 2,
        "source": "Cessna 400 Corvalis TT AFM; AOPA review",
    },

    # Cirrus SR22 (normally aspirated) — IO-550-N 310hp
    "SR22": {
        "label":          "Cirrus SR22",
        "fuel_type":      "AvGas",
        "fuel_capacity":  81.0,        # 81 usable gallons
        "fuel_unit":      "gal",
        "taxi_fuel":      1.5,
        "reserve_fuel":   10.5,        # 45 min @ 14 gph
        "climb":          {"fpm": 1270, "ktas": 100, "fuel_gph": 20.0},
        "cruise_table": [
            {"fl":  60, "ktas": 172, "fuel_gph": 17.8, "power_pct": 75, "notes": "6000ft 75% — POH 171 kt 15.4 gph 65%"},
            {"fl":  80, "ktas": 176, "fuel_gph": 17.8, "power_pct": 75, "notes": "8000ft 75%"},
            {"fl": 100, "ktas": 178, "fuel_gph": 17.0, "power_pct": 75, "notes": "10000ft 75%"},
            {"fl": 120, "ktas": 176, "fuel_gph": 15.5, "power_pct": 65, "notes": "12000ft 65% normal cruise"},
            {"fl": 140, "ktas": 173, "fuel_gph": 13.5, "power_pct": 60, "notes": "14000ft LOP economy"},
        ],
        "descent":        {"fpm": 700, "ktas": 150, "fuel_gph": 8.0},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Cirrus SR22 POH Section 5; AOPA review confirmed figures",
    },

    # Beechcraft Bonanza G36 — IO-550-B 300hp
    "BE36": {
        "label":          "Beechcraft Bonanza G36",
        "fuel_type":      "AvGas",
        "fuel_capacity":  74.0,        # 74 usable gallons
        "fuel_unit":      "gal",
        "taxi_fuel":      1.5,
        "reserve_fuel":   9.0,         # 45 min @ 12 gph
        "climb":          {"fpm": 1100, "ktas": 95, "fuel_gph": 18.0},
        "cruise_table": [
            {"fl":  60, "ktas": 161, "fuel_gph": 16.5, "power_pct": 75, "notes": "6000ft 75%"},
            {"fl":  80, "ktas": 164, "fuel_gph": 16.0, "power_pct": 75, "notes": "8000ft 75%"},
            {"fl": 100, "ktas": 165, "fuel_gph": 15.5, "power_pct": 75, "notes": "10000ft 75% best cruise"},
            {"fl": 120, "ktas": 162, "fuel_gph": 13.5, "power_pct": 65, "notes": "12000ft 65% economy"},
            {"fl": 140, "ktas": 158, "fuel_gph": 11.5, "power_pct": 55, "notes": "14000ft LRC"},
        ],
        "descent":        {"fpm": 650, "ktas": 140, "fuel_gph": 7.5},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Beechcraft Bonanza G36 POH Section 5",
    },

    # Piper PA-18 Super Cub — O-360 150hp
    "PA18": {
        "label":          "Piper PA-18 Super Cub",
        "fuel_type":      "AvGas",
        "fuel_capacity":  36.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      0.5,
        "reserve_fuel":   4.0,
        "climb":          {"fpm": 960, "ktas": 55, "fuel_gph": 9.0},
        "cruise_table": [
            {"fl":  20, "ktas":  80, "fuel_gph": 7.5, "power_pct": 75, "notes": "2000ft cruise"},
            {"fl":  45, "ktas":  82, "fuel_gph": 7.2, "power_pct": 75, "notes": "4500ft cruise"},
            {"fl":  65, "ktas":  83, "fuel_gph": 6.8, "power_pct": 70, "notes": "6500ft"},
        ],
        "descent":        {"fpm": 400, "ktas": 75, "fuel_gph": 4.0},
        "contingency_pct": 10,
        "tier": 2,
        "source": "Piper PA-18 POH; manufacturer specs",
    },

    # Piper PA-28 family — shared POH data (Warrior, Arrow, Turbo Arrow)
    "PA28": {
        "label":          "Piper PA-28 Arrow/Warrior",
        "fuel_type":      "AvGas",
        "fuel_capacity":  50.0,        # Arrow: 50 usable
        "fuel_unit":      "gal",
        "taxi_fuel":      1.0,
        "reserve_fuel":   6.0,
        "climb":          {"fpm": 875, "ktas": 85, "fuel_gph": 11.5},
        "cruise_table": [
            {"fl":  40, "ktas": 128, "fuel_gph": 10.0, "power_pct": 75, "notes": "4000ft 75% Arrow"},
            {"fl":  65, "ktas": 131, "fuel_gph": 10.0, "power_pct": 75, "notes": "6500ft 75%"},
            {"fl":  85, "ktas": 133, "fuel_gph":  9.5, "power_pct": 73, "notes": "8500ft"},
            {"fl": 100, "ktas": 148, "fuel_gph": 11.5, "power_pct": 75, "notes": "10000ft Turbo Arrow III"},
            {"fl": 120, "ktas": 155, "fuel_gph": 11.0, "power_pct": 73, "notes": "12000ft Turbo Arrow"},
        ],
        "descent":        {"fpm": 550, "ktas": 120, "fuel_gph": 6.0},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Piper Arrow III/IV POH; Just Flight documentation",
    },

    # Piper Comanche 250 — IO-540 250hp
    "PA24": {
        "label":          "Piper Comanche 250",
        "fuel_type":      "AvGas",
        "fuel_capacity":  60.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      1.0,
        "reserve_fuel":   7.5,
        "climb":          {"fpm": 1350, "ktas": 100, "fuel_gph": 18.0},
        "cruise_table": [
            {"fl":  60, "ktas": 160, "fuel_gph": 15.5, "power_pct": 75, "notes": "6000ft 75%"},
            {"fl":  85, "ktas": 164, "fuel_gph": 15.0, "power_pct": 75, "notes": "8500ft 75% best cruise"},
            {"fl": 100, "ktas": 163, "fuel_gph": 13.5, "power_pct": 65, "notes": "10000ft 65%"},
        ],
        "descent":        {"fpm": 650, "ktas": 140, "fuel_gph": 7.5},
        "contingency_pct": 10,
        "tier": 2,
        "source": "Piper Comanche 250 POH; A2A documentation",
    },

    # Beechcraft Baron G58 — 2x IO-550-C 300hp each
    "BE58": {
        "label":          "Beechcraft Baron G58",
        "fuel_type":      "AvGas",
        "fuel_capacity":  166.0,       # 166 usable gallons standard tanks
        "fuel_unit":      "gal",
        "taxi_fuel":      2.0,
        "reserve_fuel":   15.0,        # 45 min @ 20 gph both engines
        "climb":          {"fpm": 1693, "ktas": 115, "fuel_gph": 30.0},
        "cruise_table": [
            # Source: Baron 58 POH Section 5; AOPA review; Aviation Consumer
            {"fl":  60, "ktas": 185, "fuel_gph": 34.0, "power_pct": 75, "notes": "6000ft 75% — 195 kt 34 gph max"},
            {"fl":  80, "ktas": 189, "fuel_gph": 32.5, "power_pct": 75, "notes": "8000ft 75% best cruise"},
            {"fl": 100, "ktas": 190, "fuel_gph": 32.0, "power_pct": 75, "notes": "10000ft 75%"},
            {"fl": 120, "ktas": 185, "fuel_gph": 28.0, "power_pct": 65, "notes": "12000ft 65% — 180-185 kt typical"},
            {"fl": 140, "ktas": 178, "fuel_gph": 25.0, "power_pct": 62, "notes": "14000ft economy"},
        ],
        "descent":        {"fpm": 800, "ktas": 170, "fuel_gph": 12.0},
        "contingency_pct": 10,
        "tier": 1,
        "source": "Beechcraft Baron 58 POH; AOPA review; Aviation Consumer survey",
    },

    # Beechcraft Duke B60 — 2x TIGO-541 380hp turbocharged
    "BE60": {
        "label":          "Beechcraft Duke B60",
        "fuel_type":      "AvGas",
        "fuel_capacity":  142.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      2.0,
        "reserve_fuel":   16.0,
        "climb":          {"fpm": 1600, "ktas": 120, "fuel_gph": 40.0},
        "cruise_table": [
            {"fl": 100, "ktas": 215, "fuel_gph": 36.0, "power_pct": 75, "notes": "10000ft 75%"},
            {"fl": 150, "ktas": 225, "fuel_gph": 34.0, "power_pct": 75, "notes": "15000ft 75%"},
            {"fl": 200, "ktas": 230, "fuel_gph": 32.0, "power_pct": 75, "notes": "20000ft 75% max cruise"},
            {"fl": 250, "ktas": 220, "fuel_gph": 26.0, "power_pct": 65, "notes": "25000ft 65% LRC"},
        ],
        "descent":        {"fpm": 1100, "ktas": 180, "fuel_gph": 14.0},
        "contingency_pct": 10,
        "tier": 2,
        "source": "Beechcraft Duke B60 POH; Black Square documentation",
    },

    # Aerostar 600 — 2x IO-540 290hp
    "AEST": {
        "label":          "Aerostar 600",
        "fuel_type":      "AvGas",
        "fuel_capacity":  120.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      1.5,
        "reserve_fuel":   13.0,
        "climb":          {"fpm": 1800, "ktas": 130, "fuel_gph": 30.0},
        "cruise_table": [
            {"fl": 100, "ktas": 220, "fuel_gph": 26.0, "power_pct": 75, "notes": "10000ft 75%"},
            {"fl": 150, "ktas": 232, "fuel_gph": 25.0, "power_pct": 75, "notes": "15000ft"},
            {"fl": 200, "ktas": 235, "fuel_gph": 24.0, "power_pct": 75, "notes": "20000ft best cruise"},
        ],
        "descent":        {"fpm": 1000, "ktas": 180, "fuel_gph": 12.0},
        "contingency_pct": 10,
        "tier": 2,
        "source": "Aerostar 600 AFM; A2A Simulations documentation",
    },

    # ════════════════════════════════════════════════════════
    # TURBOPROPS
    # ════════════════════════════════════════════════════════

    # Daher TBM 930 — PT6A-66D 850shp
    "TBM9": {
        "label":          "Daher TBM 930",
        "fuel_type":      "JetA",
        "fuel_capacity":  282.0,       # 282 gal usable
        "fuel_unit":      "gal",
        "taxi_fuel":      4.0,
        "reserve_fuel":   40.0,        # 45 min @ 35 gph LRC
        "climb":          {"fpm": 2400, "ktas": 170, "fuel_gph": 80.0},
        "cruise_table": [
            # Source: AOPA TBM 900 review; Flying Magazine TBM 930 flight test
            {"fl": 100, "ktas": 270, "fuel_gph": 75.0, "power_pct": 100, "notes": "FL100 100% torque"},
            {"fl": 150, "ktas": 290, "fuel_gph": 70.0, "power_pct": 100, "notes": "FL150 100% torque"},
            {"fl": 200, "ktas": 310, "fuel_gph": 65.0, "power_pct": 100, "notes": "FL200 100% torque"},
            {"fl": 250, "ktas": 320, "fuel_gph": 60.0, "power_pct": 100, "notes": "FL250 100% torque ~323 KTAS"},
            {"fl": 280, "ktas": 323, "fuel_gph": 64.0, "power_pct": 100, "notes": "FL280 max cruise — 323 KTAS 64 gph"},
            {"fl": 310, "ktas": 290, "fuel_gph": 35.0, "power_pct": 75,  "notes": "FL310 LRC — 290 KTAS 35 gph"},
            {"fl": 310, "ktas": 250, "fuel_gph": 30.0, "power_pct": 60,  "notes": "FL310 economy — 250 KTAS 30 gph"},
        ],
        "descent":        {"fpm": 1500, "ktas": 220, "fuel_gph": 25.0},
        "contingency_pct": 5,
        "tier": 1,
        "source": "AOPA TBM 900 review; Flying Magazine TBM 930 flight test; Daher PIM",
    },

    # Daher TBM 850 — PT6A-66D 850shp (same engine, earlier airframe)
    "TBM8": {
        "label":          "Daher TBM 850",
        "fuel_type":      "JetA",
        "fuel_capacity":  282.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      4.0,
        "reserve_fuel":   40.0,
        "climb":          {"fpm": 1650, "ktas": 160, "fuel_gph": 75.0},
        "cruise_table": [
            {"fl": 200, "ktas": 290, "fuel_gph": 62.0, "power_pct": 100, "notes": "FL200 max cruise"},
            {"fl": 250, "ktas": 305, "fuel_gph": 60.0, "power_pct": 100, "notes": "FL250 max cruise"},
            {"fl": 280, "ktas": 320, "fuel_gph": 60.0, "power_pct": 100, "notes": "FL280 320 KTAS max cruise"},
            {"fl": 310, "ktas": 270, "fuel_gph": 35.0, "power_pct": 70,  "notes": "FL310 LRC"},
        ],
        "descent":        {"fpm": 1500, "ktas": 200, "fuel_gph": 22.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "TBM 850 published specs; cross-referenced with 930 PIM",
    },

    # Pilatus PC-12 NGX — PT6E-67XP 1200shp FADEC
    "PC12": {
        "label":          "Pilatus PC-12 NGX",
        "fuel_type":      "JetA",
        "fuel_capacity":  402.0,       # 402 gal usable per AOPA spec sheet
        "fuel_unit":      "gal",
        "taxi_fuel":      5.0,
        "reserve_fuel":   52.0,        # 45 min @ ~45 gph cruise
        "climb":          {"fpm": 1920, "ktas": 140, "fuel_gph": 78.0},
        "cruise_table": [
            # Source: AOPA PC-12 NGX review — 414 pph @ FL270; Flying Magazine
            # 518 pph climb at FL140; Wikipedia 66 gph average block
            {"fl": 100, "ktas": 260, "fuel_gph": 80.0, "power_pct": 100, "notes": "FL100 max cruise"},
            {"fl": 150, "ktas": 275, "fuel_gph": 74.0, "power_pct": 100, "notes": "FL150 max cruise"},
            {"fl": 200, "ktas": 282, "fuel_gph": 68.0, "power_pct": 100, "notes": "FL200 max cruise"},
            {"fl": 250, "ktas": 285, "fuel_gph": 62.0, "power_pct": 100, "notes": "FL250 290 KTAS max — 62 gph"},
            {"fl": 270, "ktas": 282, "fuel_gph": 62.0, "power_pct": 100, "notes": "FL270 414 pph = 62 gph per AOPA test"},
            {"fl": 280, "ktas": 278, "fuel_gph": 55.0, "power_pct": 85,  "notes": "FL280 normal cruise"},
            {"fl": 300, "ktas": 265, "fuel_gph": 48.0, "power_pct": 75,  "notes": "FL300 economy"},
            {"fl": 300, "ktas": 225, "fuel_gph": 38.0, "power_pct": 60,  "notes": "FL300 LRC — 225 KTAS 38 gph"},
        ],
        "descent":        {"fpm": 1800, "ktas": 220, "fuel_gph": 30.0},
        "contingency_pct": 5,
        "tier": 1,
        "source": "AOPA PC-12 NGX review (414 pph FL270); Flying Magazine; Pilatus specs",
    },

    # Black Square Cessna Caravan — PT6A-114A 675shp
    "C208": {
        "label":          "Cessna 208B Grand Caravan",
        "fuel_type":      "JetA",
        "fuel_capacity":  332.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      4.0,
        "reserve_fuel":   45.0,
        "climb":          {"fpm": 975, "ktas": 110, "fuel_gph": 55.0},
        "cruise_table": [
            {"fl":  80, "ktas": 175, "fuel_gph": 40.0, "power_pct": 85, "notes": "8000ft normal cruise"},
            {"fl": 100, "ktas": 180, "fuel_gph": 38.0, "power_pct": 85, "notes": "FL100 normal cruise"},
            {"fl": 150, "ktas": 185, "fuel_gph": 35.0, "power_pct": 80, "notes": "FL150"},
            {"fl": 200, "ktas": 175, "fuel_gph": 30.0, "power_pct": 70, "notes": "FL200 LRC"},
        ],
        "descent":        {"fpm": 800, "ktas": 150, "fuel_gph": 20.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Cessna 208B AFM; Black Square documentation",
    },

    # DHC-6 Twin Otter — 2x PT6A-27 620shp
    "DHC6": {
        "label":          "DHC-6 Twin Otter",
        "fuel_type":      "JetA",
        "fuel_capacity":  384.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      5.0,
        "reserve_fuel":   50.0,
        "climb":          {"fpm": 1600, "ktas": 110, "fuel_gph": 90.0},
        "cruise_table": [
            {"fl":  60, "ktas": 160, "fuel_gph": 66.0, "power_pct": 90, "notes": "6000ft normal cruise"},
            {"fl": 100, "ktas": 168, "fuel_gph": 62.0, "power_pct": 90, "notes": "FL100"},
            {"fl": 150, "ktas": 170, "fuel_gph": 56.0, "power_pct": 85, "notes": "FL150 best cruise"},
        ],
        "descent":        {"fpm": 900, "ktas": 140, "fuel_gph": 30.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "de Havilland DHC-6 AFM; manufacturer published specs",
    },

    # Beechcraft King Air C90 GTX — 2x PT6A-135A 550shp
    "BE9L": {
        "label":          "Beechcraft King Air C90 GTX",
        "fuel_type":      "JetA",
        "fuel_capacity":  384.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      6.0,
        "reserve_fuel":   48.0,
        "climb":          {"fpm": 1965, "ktas": 150, "fuel_gph": 100.0},
        "cruise_table": [
            {"fl": 120, "ktas": 226, "fuel_gph": 72.0, "power_pct": 85, "notes": "FL120 high speed"},
            {"fl": 180, "ktas": 230, "fuel_gph": 68.0, "power_pct": 82, "notes": "FL180 max cruise"},
            {"fl": 220, "ktas": 226, "fuel_gph": 60.0, "power_pct": 75, "notes": "FL220 normal cruise"},
            {"fl": 250, "ktas": 218, "fuel_gph": 50.0, "power_pct": 65, "notes": "FL250 LRC"},
        ],
        "descent":        {"fpm": 1400, "ktas": 190, "fuel_gph": 32.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "King Air C90 AFM; Beechcraft published specs",
    },

    # ATR 72-600 — 2x PW127M 2750shp
    "AT76": {
        "label":          "ATR 72-600",
        "fuel_type":      "JetA",
        "fuel_capacity":  1350.0,      # ~1350 gal usable
        "fuel_unit":      "gal",
        "taxi_fuel":      15.0,
        "reserve_fuel":   175.0,
        "climb":          {"fpm": 1200, "ktas": 175, "fuel_gph": 240.0},
        "cruise_table": [
            {"fl": 170, "ktas": 275, "fuel_gph": 185.0, "power_pct": 90, "notes": "FL170 — typical ops altitude"},
            {"fl": 200, "ktas": 277, "fuel_gph": 178.0, "power_pct": 90, "notes": "FL200 normal cruise"},
            {"fl": 250, "ktas": 270, "fuel_gph": 162.0, "power_pct": 85, "notes": "FL250 — 270 KTAS max cruise"},
        ],
        "descent":        {"fpm": 1400, "ktas": 220, "fuel_gph": 80.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "ATR 72-600 FCOM; manufacturer published specs",
    },

    # Cessna 408 SkyCourier — PT6A-65B 1100shp
    "C408": {
        "label":          "Cessna 408 SkyCourier",
        "fuel_type":      "JetA",
        "fuel_capacity":  400.0,
        "fuel_unit":      "gal",
        "taxi_fuel":      5.0,
        "reserve_fuel":   52.0,
        "climb":          {"fpm": 1200, "ktas": 140, "fuel_gph": 80.0},
        "cruise_table": [
            {"fl": 100, "ktas": 190, "fuel_gph": 70.0, "power_pct": 90, "notes": "FL100"},
            {"fl": 150, "ktas": 198, "fuel_gph": 65.0, "power_pct": 88, "notes": "FL150 normal cruise"},
            {"fl": 200, "ktas": 200, "fuel_gph": 60.0, "power_pct": 85, "notes": "FL200 — 200 KTAS published"},
        ],
        "descent":        {"fpm": 1000, "ktas": 165, "fuel_gph": 28.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Cessna 408 SkyCourier AFM; manufacturer specs",
    },

    # Turbine Duke (Black Square) — PT6A-34 680shp (twin turbine conversion)
    # Note: not a factory type — based on Soloy/other turbine Duke conversions
    # "BE60" simbrief_code shared with piston Duke — same key, turbine variant
    # Handled by aircraft profile label; POH data here is for turbine variant

    # ════════════════════════════════════════════════════════
    # BUSINESS JETS
    # ════════════════════════════════════════════════════════

    # Cirrus Vision SF50 — Williams FJ33-5A 1,800 lbf
    "SF50": {
        "label":          "Cirrus Vision Jet SF50",
        "fuel_type":      "JetA",
        "fuel_capacity":  1895.0,      # 1895 lbs usable
        "fuel_unit":      "lbs",
        "taxi_fuel":      80.0,
        "reserve_fuel":   360.0,       # 45 min IFR
        "climb":          {"fpm": 1550, "ktas": 185, "fuel_pph": 680.0},
        "cruise_table": [
            {"fl": 200, "ktas": 275, "fuel_pph": 430.0, "power_pct": 95, "notes": "FL200 normal cruise"},
            {"fl": 250, "ktas": 300, "fuel_pph": 410.0, "power_pct": 95, "notes": "FL250 normal cruise"},
            {"fl": 280, "ktas": 311, "fuel_pph": 395.0, "power_pct": 95, "notes": "FL280 max cruise — 311 KTAS"},
            {"fl": 280, "ktas": 275, "fuel_pph": 305.0, "power_pct": 75, "notes": "FL280 LRC — ~45 gph"},
        ],
        "descent":        {"fpm": 1500, "ktas": 250, "fuel_pph": 200.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Cirrus Vision Jet SF50 AFM; operator reviews; FlightFX documentation",
    },

    # Cessna Citation CJ4 — 2x Williams FJ44-4A 3,621 lbf each
    # simbrief_code in aircraft.py is "C25C" (ICAO code for CJ4)
    "C25C": {
        "label":          "Cessna Citation CJ4",
        "fuel_type":      "JetA",
        "fuel_capacity":  5828.0,      # 5828 lbs / 870 gal
        "fuel_unit":      "lbs",
        "taxi_fuel":      200.0,
        "reserve_fuel":   900.0,       # 45 min IFR reserve
        "climb":          {"fpm": 3854, "ktas": 250, "fuel_pph": 1200.0},
        "cruise_table": [
            # Source: Flying Magazine CJ4 flight test; Flight Global CJ4 test
            # FL400: M0.76 = 440 KTAS, 558 kg/hr total = 1230 pph
            # FL400 LRC: M0.586 = 339 KTAS, 344 kg/hr = 759 pph
            # FL310 max: 453 KTAS; FL450 max: 425 KTAS at M0.75 = 1040 pph
            {"fl": 310, "ktas": 453, "fuel_pph":  800.0, "power_pct": 100, "notes": "FL310 max cruise — 453 KTAS"},
            {"fl": 370, "ktas": 445, "fuel_pph":  900.0, "power_pct": 100, "notes": "FL370 high cruise M0.75"},
            {"fl": 400, "ktas": 440, "fuel_pph": 1230.0, "power_pct": 100, "notes": "FL400 high speed — M0.76 558 kg/hr"},
            {"fl": 400, "ktas": 339, "fuel_pph":  759.0, "power_pct":  65, "notes": "FL400 LRC — M0.586 344 kg/hr"},
            {"fl": 450, "ktas": 425, "fuel_pph": 1040.0, "power_pct": 100, "notes": "FL450 max — M0.75 1040 pph"},
            {"fl": 450, "ktas": 390, "fuel_pph":  800.0, "power_pct":  80, "notes": "FL450 normal cruise"},
        ],
        "descent":        {"fpm": 2500, "ktas": 300, "fuel_pph": 400.0},
        "contingency_pct": 5,
        "tier": 1,
        "source": "Flying Magazine CJ4 flight test; Flight Global CJ4 test (558 kg/hr FL400)",
    },

    # Pilatus PC-24 — 2x Williams FJ44-4A 3,400 lbf each
    "PC24": {
        "label":          "Pilatus PC-24",
        "fuel_type":      "JetA",
        "fuel_capacity":  6217.0,      # 6217 lbs usable
        "fuel_unit":      "lbs",
        "taxi_fuel":      200.0,
        "reserve_fuel":   950.0,
        "climb":          {"fpm": 4000, "ktas": 260, "fuel_pph": 1400.0},
        "cruise_table": [
            {"fl": 350, "ktas": 440, "fuel_pph": 1200.0, "power_pct": 100, "notes": "FL350 high cruise"},
            {"fl": 390, "ktas": 445, "fuel_pph": 1150.0, "power_pct": 100, "notes": "FL390 max cruise — 440 KTAS"},
            {"fl": 450, "ktas": 430, "fuel_pph": 1050.0, "power_pct":  90, "notes": "FL450 normal cruise"},
            {"fl": 450, "ktas": 380, "fuel_pph":  850.0, "power_pct":  75, "notes": "FL450 LRC"},
        ],
        "descent":        {"fpm": 2500, "ktas": 310, "fuel_pph": 420.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Pilatus PC-24 published specs; AOPA review",
    },

    # HondaJet Elite II — 2x GE Honda HF120 2,095 lbf each
    "HN700": {
        "label":          "HondaJet Elite II",
        "fuel_type":      "JetA",
        "fuel_capacity":  3145.0,      # ~3145 lbs usable
        "fuel_unit":      "lbs",
        "taxi_fuel":      120.0,
        "reserve_fuel":   600.0,
        "climb":          {"fpm": 3990, "ktas": 250, "fuel_pph": 1100.0},
        "cruise_table": [
            {"fl": 350, "ktas": 420, "fuel_pph": 900.0, "power_pct": 100, "notes": "FL350 high cruise"},
            {"fl": 390, "ktas": 422, "fuel_pph": 870.0, "power_pct": 100, "notes": "FL390 max cruise — 422 KTAS"},
            {"fl": 430, "ktas": 418, "fuel_pph": 840.0, "power_pct":  95, "notes": "FL430 normal cruise"},
            {"fl": 430, "ktas": 380, "fuel_pph": 700.0, "power_pct":  78, "notes": "FL430 LRC"},
        ],
        "descent":        {"fpm": 2200, "ktas": 290, "fuel_pph": 350.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Honda Aircraft Company published specs; AOPA review",
    },

    # BAe 146 / Avro RJ — 4x LF507 7,000 lbf each
    "B461": {
        "label":          "BAe 146-100",
        "fuel_type":      "JetA",
        "fuel_capacity":  25600.0,     # ~25,600 lbs usable
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   3000.0,
        "climb":          {"fpm": 3000, "ktas": 270, "fuel_pph": 8000.0},
        "cruise_table": [
            {"fl": 250, "ktas": 395, "fuel_pph": 5600.0, "power_pct": 90, "notes": "FL250 normal cruise"},
            {"fl": 310, "ktas": 408, "fuel_pph": 5200.0, "power_pct": 88, "notes": "FL310 high cruise"},
            {"fl": 350, "ktas": 400, "fuel_pph": 4800.0, "power_pct": 85, "notes": "FL350 max cruise — ~400 KTAS"},
        ],
        "descent":        {"fpm": 1800, "ktas": 300, "fuel_pph": 1600.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "BAe 146 FCOM; Just Flight documentation",
    },

    "RJ1H": {
        "label":          "Avro RJ100",
        "fuel_type":      "JetA",
        "fuel_capacity":  25600.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   3000.0,
        "climb":          {"fpm": 2800, "ktas": 270, "fuel_pph": 8000.0},
        "cruise_table": [
            {"fl": 250, "ktas": 395, "fuel_pph": 5600.0, "power_pct": 90, "notes": "FL250"},
            {"fl": 310, "ktas": 405, "fuel_pph": 5100.0, "power_pct": 88, "notes": "FL310 max cruise"},
        ],
        "descent":        {"fpm": 1800, "ktas": 300, "fuel_pph": 1600.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Avro RJ100 FCOM; Just Flight documentation",
    },

    # Fokker F28 — 2x Spey Mk 555 9,900 lbf each
    "F28": {
        "label":          "Fokker F28 Fellowship",
        "fuel_type":      "JetA",
        "fuel_capacity":  19000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      400.0,
        "reserve_fuel":   2500.0,
        "climb":          {"fpm": 2800, "ktas": 280, "fuel_pph": 8000.0},
        "cruise_table": [
            {"fl": 250, "ktas": 390, "fuel_pph": 5800.0, "power_pct": 88, "notes": "FL250"},
            {"fl": 310, "ktas": 408, "fuel_pph": 5400.0, "power_pct": 88, "notes": "FL310 normal"},
            {"fl": 350, "ktas": 415, "fuel_pph": 5200.0, "power_pct": 85, "notes": "FL350 max cruise"},
        ],
        "descent":        {"fpm": 2000, "ktas": 310, "fuel_pph": 1800.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Fokker F28 FCOM; Just Flight documentation",
    },

    # ════════════════════════════════════════════════════════
    # REGIONAL AIRLINERS
    # ════════════════════════════════════════════════════════

    # Airbus A220-300 (formerly Bombardier CS300) — 2x PW1500G 23,300 lbf
    "BCS3": {
        "label":          "Airbus A220-300",
        "fuel_type":      "JetA",
        "fuel_capacity":  21805.0,     # ~21,805 lbs usable
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   3000.0,
        "climb":          {"fpm": 2800, "ktas": 300, "fuel_pph": 10000.0},
        "cruise_table": [
            {"fl": 350, "ktas": 451, "fuel_pph": 6800.0, "power_pct": 88, "notes": "FL350 normal cruise"},
            {"fl": 390, "ktas": 453, "fuel_pph": 6400.0, "power_pct": 85, "notes": "FL390 — Mach 0.82 max"},
            {"fl": 410, "ktas": 440, "fuel_pph": 6200.0, "power_pct": 82, "notes": "FL410 economy"},
        ],
        "descent":        {"fpm": 2000, "ktas": 320, "fuel_pph": 2000.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "A220-300 FCOM; Airbus published specs",
    },

    # Embraer E175 — 2x GE CF34-8E5 14,200 lbf each
    "E170": {
        "label":          "Embraer E175",
        "fuel_type":      "JetA",
        "fuel_capacity":  26800.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      400.0,
        "reserve_fuel":   3200.0,
        "climb":          {"fpm": 2700, "ktas": 290, "fuel_pph": 9500.0},
        "cruise_table": [
            {"fl": 330, "ktas": 436, "fuel_pph": 6400.0, "power_pct": 87, "notes": "FL330 normal cruise"},
            {"fl": 370, "ktas": 436, "fuel_pph": 6000.0, "power_pct": 85, "notes": "FL370"},
            {"fl": 410, "ktas": 425, "fuel_pph": 5700.0, "power_pct": 82, "notes": "FL410 — Mach 0.82 max"},
        ],
        "descent":        {"fpm": 2000, "ktas": 310, "fuel_pph": 1800.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Embraer E175 FCOM; published specs",
    },

    # Saab 340B — 2x CT7-9B 1,870shp
    "SF34": {
        "label":          "Saab 340B",
        "fuel_type":      "JetA",
        "fuel_capacity":  1350.0,      # ~1350 gal usable
        "fuel_unit":      "gal",
        "taxi_fuel":      12.0,
        "reserve_fuel":   160.0,
        "climb":          {"fpm": 1600, "ktas": 180, "fuel_gph": 240.0},
        "cruise_table": [
            {"fl": 150, "ktas": 250, "fuel_gph": 175.0, "power_pct": 90, "notes": "FL150"},
            {"fl": 200, "ktas": 258, "fuel_gph": 165.0, "power_pct": 90, "notes": "FL200 — typical ops"},
            {"fl": 250, "ktas": 255, "fuel_gph": 155.0, "power_pct": 87, "notes": "FL250 max cruise — 250 KTAS"},
        ],
        "descent":        {"fpm": 1400, "ktas": 210, "fuel_gph": 70.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Saab 340B AFM; manufacturer published specs",
    },

    # ════════════════════════════════════════════════════════
    # NARROWBODY AIRLINERS
    # ════════════════════════════════════════════════════════

    # Boeing 737 MAX 8 — 2x CFM LEAP-1B 28,000 lbf each
    "B38M": {
        "label":          "Boeing 737 MAX 8",
        "fuel_type":      "JetA",
        "fuel_capacity":  46063.0,     # 46,063 lbs usable
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   5500.0,
        "climb":          {"fpm": 2500, "ktas": 290, "fuel_pph": 16000.0},
        "cruise_table": [
            {"fl": 330, "ktas": 453, "fuel_pph": 9500.0, "power_pct": 85, "notes": "FL330 normal CI50"},
            {"fl": 350, "ktas": 453, "fuel_pph": 9000.0, "power_pct": 85, "notes": "FL350 typical cruise"},
            {"fl": 370, "ktas": 453, "fuel_pph": 8500.0, "power_pct": 82, "notes": "FL370 step climb"},
            {"fl": 390, "ktas": 438, "fuel_pph": 8000.0, "power_pct": 78, "notes": "FL390 high altitude"},
            {"fl": 410, "ktas": 420, "fuel_pph": 7500.0, "power_pct": 75, "notes": "FL410 max ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 320, "fuel_pph": 2200.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Boeing 737 MAX 8 FCOM; published airline operations data",
    },

    # Boeing 737 NG -600
    "B736": {
        "label":          "Boeing 737-600",
        "fuel_type":      "JetA",
        "fuel_capacity":  46063.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   5200.0,
        "climb":          {"fpm": 2500, "ktas": 290, "fuel_pph": 14000.0},
        "cruise_table": [
            {"fl": 330, "ktas": 448, "fuel_pph": 8800.0, "power_pct": 85, "notes": "FL330"},
            {"fl": 350, "ktas": 448, "fuel_pph": 8400.0, "power_pct": 85, "notes": "FL350 typical"},
            {"fl": 370, "ktas": 448, "fuel_pph": 8000.0, "power_pct": 82, "notes": "FL370"},
            {"fl": 410, "ktas": 420, "fuel_pph": 7200.0, "power_pct": 75, "notes": "FL410 ECON"},
        ],
        "descent":        {"fpm": 2000, "ktas": 310, "fuel_pph": 2000.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Boeing 737-600 FCOM; PMDG documentation",
    },

    # Boeing 737-800
    "B738": {
        "label":          "Boeing 737-800",
        "fuel_type":      "JetA",
        "fuel_capacity":  46063.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   5500.0,
        "climb":          {"fpm": 2500, "ktas": 290, "fuel_pph": 15000.0},
        "cruise_table": [
            {"fl": 330, "ktas": 450, "fuel_pph": 9200.0, "power_pct": 85, "notes": "FL330 CI50"},
            {"fl": 350, "ktas": 450, "fuel_pph": 8800.0, "power_pct": 85, "notes": "FL350 typical cruise"},
            {"fl": 370, "ktas": 450, "fuel_pph": 8400.0, "power_pct": 82, "notes": "FL370"},
            {"fl": 390, "ktas": 435, "fuel_pph": 8000.0, "power_pct": 78, "notes": "FL390"},
            {"fl": 410, "ktas": 418, "fuel_pph": 7600.0, "power_pct": 75, "notes": "FL410 ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 320, "fuel_pph": 2200.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Boeing 737-800 FCOM; PMDG documentation",
    },

    # Boeing 737-900
    "B739": {
        "label":          "Boeing 737-900",
        "fuel_type":      "JetA",
        "fuel_capacity":  46063.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   5500.0,
        "climb":          {"fpm": 2500, "ktas": 290, "fuel_pph": 15500.0},
        "cruise_table": [
            {"fl": 330, "ktas": 450, "fuel_pph": 9400.0, "power_pct": 85, "notes": "FL330"},
            {"fl": 350, "ktas": 450, "fuel_pph": 9000.0, "power_pct": 85, "notes": "FL350 typical"},
            {"fl": 370, "ktas": 450, "fuel_pph": 8500.0, "power_pct": 82, "notes": "FL370"},
            {"fl": 410, "ktas": 420, "fuel_pph": 7700.0, "power_pct": 75, "notes": "FL410 ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 320, "fuel_pph": 2200.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Boeing 737-900 FCOM; PMDG documentation",
    },

    # Airbus A320neo — CFM LEAP-1A or PW1100G ~30,000 lbf each
    "A20N": {
        "label":          "Airbus A320neo",
        "fuel_type":      "JetA",
        "fuel_capacity":  42000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   5000.0,
        "climb":          {"fpm": 2000, "ktas": 290, "fuel_pph": 14000.0},
        "cruise_table": [
            {"fl": 330, "ktas": 450, "fuel_pph": 9000.0,  "power_pct": 85, "notes": "FL330 CI100"},
            {"fl": 350, "ktas": 454, "fuel_pph": 8500.0,  "power_pct": 85, "notes": "FL350 typical cruise"},
            {"fl": 370, "ktas": 450, "fuel_pph": 8000.0,  "power_pct": 82, "notes": "FL370"},
            {"fl": 390, "ktas": 440, "fuel_pph": 7500.0,  "power_pct": 78, "notes": "FL390 ECON"},
            {"fl": 410, "ktas": 425, "fuel_pph": 7200.0,  "power_pct": 75, "notes": "FL410 max ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 300, "fuel_pph": 2000.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "A320neo FCOM; Airbus performance data; FlyByWire documentation",
    },

    # A320ceo (Fenix) — CFM56-5B ~27,000 lbf each
    "A320": {
        "label":          "Airbus A320ceo",
        "fuel_type":      "JetA",
        "fuel_capacity":  42000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   5000.0,
        "climb":          {"fpm": 1800, "ktas": 290, "fuel_pph": 15000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 448, "fuel_pph": 9500.0,  "power_pct": 87, "notes": "FL310 typical"},
            {"fl": 330, "ktas": 450, "fuel_pph": 9200.0,  "power_pct": 85, "notes": "FL330 normal cruise"},
            {"fl": 350, "ktas": 450, "fuel_pph": 8800.0,  "power_pct": 85, "notes": "FL350"},
            {"fl": 370, "ktas": 445, "fuel_pph": 8400.0,  "power_pct": 82, "notes": "FL370 step"},
            {"fl": 390, "ktas": 435, "fuel_pph": 8000.0,  "power_pct": 78, "notes": "FL390 max ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 300, "fuel_pph": 2200.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "A320 FCOM; Fenix Simulations documentation",
    },

    # A319ceo (Fenix)
    "A319": {
        "label":          "Airbus A319ceo",
        "fuel_type":      "JetA",
        "fuel_capacity":  38000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      500.0,
        "reserve_fuel":   4800.0,
        "climb":          {"fpm": 2000, "ktas": 290, "fuel_pph": 13000.0},
        "cruise_table": [
            {"fl": 330, "ktas": 448, "fuel_pph": 8800.0, "power_pct": 85, "notes": "FL330 normal cruise"},
            {"fl": 350, "ktas": 448, "fuel_pph": 8400.0, "power_pct": 85, "notes": "FL350"},
            {"fl": 390, "ktas": 430, "fuel_pph": 7800.0, "power_pct": 78, "notes": "FL390 ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 300, "fuel_pph": 2000.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "A319 FCOM; Fenix Simulations documentation",
    },

    # A321LR — CFM LEAP-1A/PW1100G ~33,000 lbf each
    "A21N": {
        "label":          "Airbus A321LR",
        "fuel_type":      "JetA",
        "fuel_capacity":  54500.0,     # ACT tanks for LR variant
        "fuel_unit":      "lbs",
        "taxi_fuel":      600.0,
        "reserve_fuel":   5800.0,
        "climb":          {"fpm": 2000, "ktas": 290, "fuel_pph": 16000.0},
        "cruise_table": [
            {"fl": 330, "ktas": 450, "fuel_pph": 10000.0, "power_pct": 85, "notes": "FL330 normal"},
            {"fl": 350, "ktas": 454, "fuel_pph": 9500.0,  "power_pct": 85, "notes": "FL350 typical"},
            {"fl": 390, "ktas": 445, "fuel_pph": 8800.0,  "power_pct": 80, "notes": "FL390 ECON"},
            {"fl": 410, "ktas": 430, "fuel_pph": 8400.0,  "power_pct": 77, "notes": "FL410 max"},
        ],
        "descent":        {"fpm": 1800, "ktas": 300, "fuel_pph": 2200.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "A321LR FCOM; Airbus published specs",
    },

    # FlyByWire A32NX (same as A20N performance)
    # "A20N" key already covers this — no duplicate needed

    # ════════════════════════════════════════════════════════
    # WIDEBODY AIRLINERS
    # ════════════════════════════════════════════════════════

    # Boeing 787-10 — 2x GE GEnx-1B 76,100 lbf each
    "B78X": {
        "label":          "Boeing 787-10 Dreamliner",
        "fuel_type":      "JetA",
        "fuel_capacity":  223000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      1500.0,
        "reserve_fuel":   20000.0,
        "climb":          {"fpm": 2200, "ktas": 310, "fuel_pph": 45000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 488, "fuel_pph": 28000.0, "power_pct": 90, "notes": "FL310 initial cruise"},
            {"fl": 330, "ktas": 492, "fuel_pph": 26000.0, "power_pct": 88, "notes": "FL330 normal"},
            {"fl": 350, "ktas": 492, "fuel_pph": 24000.0, "power_pct": 85, "notes": "FL350 typical"},
            {"fl": 390, "ktas": 478, "fuel_pph": 22000.0, "power_pct": 80, "notes": "FL390 ECON"},
            {"fl": 430, "ktas": 460, "fuel_pph": 20000.0, "power_pct": 75, "notes": "FL430 max ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 350, "fuel_pph": 5000.0},
        "contingency_pct": 3,
        "tier": 2,
        "source": "Boeing 787-10 FCOM; published airline data",
    },

    # Airbus A330-300 — 2x Rolls-Royce Trent 772B 71,100 lbf each
    "A333": {
        "label":          "Airbus A330-300",
        "fuel_type":      "JetA",
        "fuel_capacity":  194000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      1500.0,
        "reserve_fuel":   18000.0,
        "climb":          {"fpm": 2000, "ktas": 300, "fuel_pph": 40000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 480, "fuel_pph": 26000.0, "power_pct": 90, "notes": "FL310 initial"},
            {"fl": 330, "ktas": 484, "fuel_pph": 24000.0, "power_pct": 88, "notes": "FL330 normal cruise"},
            {"fl": 350, "ktas": 484, "fuel_pph": 22000.0, "power_pct": 85, "notes": "FL350"},
            {"fl": 370, "ktas": 478, "fuel_pph": 20500.0, "power_pct": 82, "notes": "FL370 step"},
            {"fl": 410, "ktas": 460, "fuel_pph": 19000.0, "power_pct": 78, "notes": "FL410 ECON"},
        ],
        "descent":        {"fpm": 1800, "ktas": 340, "fuel_pph": 5000.0},
        "contingency_pct": 3,
        "tier": 2,
        "source": "A330-300 FCOM; iniBuilds documentation",
    },

    # Boeing 777-200ER — 2x GE90-94B 93,700 lbf each
    "B772": {
        "label":          "Boeing 777-200ER",
        "fuel_type":      "JetA",
        "fuel_capacity":  280000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      1800.0,
        "reserve_fuel":   22000.0,
        "climb":          {"fpm": 2000, "ktas": 320, "fuel_pph": 55000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 488, "fuel_pph": 35000.0, "power_pct": 90, "notes": "FL310 initial"},
            {"fl": 330, "ktas": 492, "fuel_pph": 33000.0, "power_pct": 88, "notes": "FL330 normal"},
            {"fl": 350, "ktas": 492, "fuel_pph": 31000.0, "power_pct": 85, "notes": "FL350"},
            {"fl": 370, "ktas": 486, "fuel_pph": 29000.0, "power_pct": 82, "notes": "FL370"},
            {"fl": 410, "ktas": 466, "fuel_pph": 26000.0, "power_pct": 76, "notes": "FL410 ECON"},
        ],
        "descent":        {"fpm": 1500, "ktas": 350, "fuel_pph": 7000.0},
        "contingency_pct": 3,
        "tier": 2,
        "source": "Boeing 777-200ER FCOM; PMDG documentation",
    },

    # Boeing 777-300ER — 2x GE90-115B 115,300 lbf each
    "B77W": {
        "label":          "Boeing 777-300ER",
        "fuel_type":      "JetA",
        "fuel_capacity":  320000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      2000.0,
        "reserve_fuel":   25000.0,
        "climb":          {"fpm": 2000, "ktas": 320, "fuel_pph": 60000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 488, "fuel_pph": 38000.0, "power_pct": 90, "notes": "FL310 initial cruise"},
            {"fl": 330, "ktas": 492, "fuel_pph": 36000.0, "power_pct": 88, "notes": "FL330 normal"},
            {"fl": 350, "ktas": 492, "fuel_pph": 34000.0, "power_pct": 85, "notes": "FL350"},
            {"fl": 370, "ktas": 488, "fuel_pph": 32000.0, "power_pct": 82, "notes": "FL370 step"},
            {"fl": 390, "ktas": 480, "fuel_pph": 30000.0, "power_pct": 78, "notes": "FL390"},
            {"fl": 410, "ktas": 465, "fuel_pph": 28000.0, "power_pct": 74, "notes": "FL410 max"},
        ],
        "descent":        {"fpm": 1500, "ktas": 350, "fuel_pph": 8000.0},
        "contingency_pct": 3,
        "tier": 1,
        "source": "Boeing 777-300ER FCOM; PMDG documentation; published airline data",
    },

    # Boeing 777F — same GE90-115B, heavier MTOW
    "B77F": {
        "label":          "Boeing 777F",
        "fuel_type":      "JetA",
        "fuel_capacity":  320000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      2000.0,
        "reserve_fuel":   26000.0,
        "climb":          {"fpm": 1800, "ktas": 310, "fuel_pph": 65000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 484, "fuel_pph": 42000.0, "power_pct": 92, "notes": "FL310 initial (heavy)"},
            {"fl": 330, "ktas": 488, "fuel_pph": 39000.0, "power_pct": 88, "notes": "FL330"},
            {"fl": 350, "ktas": 488, "fuel_pph": 36000.0, "power_pct": 85, "notes": "FL350"},
            {"fl": 390, "ktas": 476, "fuel_pph": 32000.0, "power_pct": 80, "notes": "FL390"},
        ],
        "descent":        {"fpm": 1500, "ktas": 340, "fuel_pph": 8000.0},
        "contingency_pct": 3,
        "tier": 2,
        "source": "Boeing 777F FCOM; PMDG documentation",
    },

    # Boeing 747-8 — 2x GEnx-2B67 66,500 lbf each (4 engines)
    "B748": {
        "label":          "Boeing 747-8 Intercontinental",
        "fuel_type":      "JetA",
        "fuel_capacity":  406000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      2500.0,
        "reserve_fuel":   35000.0,
        "climb":          {"fpm": 1800, "ktas": 310, "fuel_pph": 80000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 488, "fuel_pph": 48000.0, "power_pct": 90, "notes": "FL310 initial"},
            {"fl": 330, "ktas": 492, "fuel_pph": 45000.0, "power_pct": 88, "notes": "FL330"},
            {"fl": 350, "ktas": 492, "fuel_pph": 42000.0, "power_pct": 85, "notes": "FL350"},
            {"fl": 390, "ktas": 475, "fuel_pph": 38000.0, "power_pct": 80, "notes": "FL390 ECON"},
        ],
        "descent":        {"fpm": 1600, "ktas": 350, "fuel_pph": 10000.0},
        "contingency_pct": 3,
        "tier": 2,
        "source": "Boeing 747-8 FCOM; published airline data",
    },

    # Airbus A380 — 4x RR Trent 970 76,500 lbf each
    "A388": {
        "label":          "Airbus A380",
        "fuel_type":      "JetA",
        "fuel_capacity":  558000.0,
        "fuel_unit":      "lbs",
        "taxi_fuel":      3000.0,
        "reserve_fuel":   48000.0,
        "climb":          {"fpm": 1800, "ktas": 310, "fuel_pph": 100000.0},
        "cruise_table": [
            {"fl": 310, "ktas": 488, "fuel_pph": 58000.0, "power_pct": 90, "notes": "FL310 initial"},
            {"fl": 330, "ktas": 492, "fuel_pph": 55000.0, "power_pct": 88, "notes": "FL330"},
            {"fl": 350, "ktas": 492, "fuel_pph": 52000.0, "power_pct": 85, "notes": "FL350 typical cruise"},
            {"fl": 390, "ktas": 478, "fuel_pph": 48000.0, "power_pct": 80, "notes": "FL390 ECON"},
        ],
        "descent":        {"fpm": 1500, "ktas": 340, "fuel_pph": 12000.0},
        "contingency_pct": 3,
        "tier": 2,
        "source": "A380 FCOM; FlyByWire documentation; published airline data",
    },

    # ════════════════════════════════════════════════════════
    # MILITARY / SPECIAL
    # ════════════════════════════════════════════════════════

    # A400M Atlas — 4x TP400-D6 11,000shp each
    "A400": {
        "label":          "Airbus A400M Atlas",
        "fuel_type":      "JetA",
        "fuel_capacity":  196000.0,    # max internal fuel ~196,000 lbs
        "fuel_unit":      "lbs",
        "taxi_fuel":      1500.0,
        "reserve_fuel":   18000.0,
        "climb":          {"fpm": 1800, "ktas": 280, "fuel_pph": 40000.0},
        "cruise_table": [
            {"fl": 250, "ktas": 360, "fuel_pph": 28000.0, "power_pct": 90, "notes": "FL250 tactical cruise"},
            {"fl": 300, "ktas": 380, "fuel_pph": 26000.0, "power_pct": 88, "notes": "FL300 normal"},
            {"fl": 370, "ktas": 390, "fuel_pph": 24000.0, "power_pct": 85, "notes": "FL370 max cruise — ~M0.72"},
        ],
        "descent":        {"fpm": 1800, "ktas": 310, "fuel_pph": 8000.0},
        "contingency_pct": 5,
        "tier": 2,
        "source": "Airbus A400M published specs; iniBuilds documentation",
    },
}


# ── Lookup helpers ─────────────────────────────────────────────

def get_poh(simbrief_code: str):
    """Return POH data for a simbrief_code, or None if not found."""
    return POH.get(simbrief_code)


def get_cruise_row(poh: dict, target_fl: int) -> dict:
    """
    Return best matching cruise row for target_fl.
    Interpolates linearly between the two nearest table entries.
    """
    table = poh.get("cruise_table", [])
    if not table:
        return {}

    # Exact match
    for r in table:
        if r["fl"] == target_fl:
            return r

    below = [r for r in table if r["fl"] <= target_fl]
    above = [r for r in table if r["fl"] >= target_fl]

    if not below:
        return table[0]
    if not above:
        return table[-1]

    r1 = max(below, key=lambda r: r["fl"])
    r2 = min(above, key=lambda r: r["fl"])

    if r1["fl"] == r2["fl"]:
        return r1

    ratio    = (target_fl - r1["fl"]) / (r2["fl"] - r1["fl"])
    fuel_key = "fuel_pph" if "fuel_pph" in r1 else "fuel_gph"

    return {
        "fl":        target_fl,
        "ktas":      round(r1["ktas"]      + ratio * (r2["ktas"]      - r1["ktas"])),
        fuel_key:    round(r1[fuel_key]    + ratio * (r2[fuel_key]    - r1[fuel_key]), 1),
        "power_pct": round(r1["power_pct"] + ratio * (r2["power_pct"] - r1["power_pct"])),
        "notes":     f"Interpolated FL{r1['fl']}–FL{r2['fl']}",
    }


def fuel_unit_label(poh: dict) -> str:
    return "lbs/hr" if poh.get("fuel_unit") == "lbs" else "gal/hr"


def fuel_display(amount: float, poh: dict) -> str:
    unit = poh.get("fuel_unit", "gal")
    if unit == "lbs":
        return f"{amount:.0f} lbs ({amount/6.7:.0f} gal)"
    fuel_type = poh.get("fuel_type", "AvGas")
    lbs_per_gal = 6.7 if fuel_type == "JetA" else 6.0
    return f"{amount:.1f} gal ({amount * lbs_per_gal:.0f} lbs)"