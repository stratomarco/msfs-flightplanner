# ============================================================
# winds_aloft.py — AWC Winds Aloft for MSFS Flight Planner
# ============================================================

import re
import math
import threading
import requests
from functools import lru_cache

_AWC_URL  = "https://aviationweather.gov/api/data/windtemp"
_HEADERS  = {"User-Agent": "MSFS-FlightPlanner/1.0 (personal sim use)"}

_LOW_LEVELS  = [3000, 6000, 9000, 12000, 18000, 24000, 30000, 34000, 39000]
_HIGH_LEVELS = [24000, 30000, 34000, 39000, 45000, 53000]


def _pick_level(cruise_fl: int) -> str:
    return "high" if cruise_fl * 100 > 24000 else "low"


@lru_cache(maxsize=4)
def _fetch_windtemp_text(level: str) -> str | None:
    """Fetch raw FD winds text from AWC, cached."""
    try:
        resp = requests.get(
            _AWC_URL,
            params={"region": "us", "level": level, "fcst": "06"},
            headers=_HEADERS,
            timeout=12,
        )
        if resp.status_code == 200 and len(resp.text) > 200:
            return resp.text
        return None
    except Exception:
        return None


# ── FD table parser ──────────────────────────────────────────

def _parse_fd_table(text: str, station_id: str, alt_ft: int) -> dict | None:
    """
    Parse AWC FD winds text for a given 3-letter station ID and altitude.
    Format example:
      FT  3000    6000    9000   12000   18000   24000  30000  34000  39000
      ABI      0311+00 3210-01 3218-04 3041-13 2950-25 296041 296351 297760
    """
    if not text:
        return None

    lines = text.splitlines()

    # ── Find header line (starts with FT or contains altitude numbers) ──
    header_alts = []
    header_idx  = None
    for i, line in enumerate(lines):
        # Match "FT  3000    6000 ..." or "FT   45000  53000"
        if re.match(r'^FT\s+\d{4,5}', line):
            header_alts = [int(x) for x in re.findall(r'\d{4,5}', line)]
            header_idx  = i
            break

    if not header_idx or not header_alts:
        return None

    # Normalise station ID — strip leading K/C/M if 4-letter ICAO
    sid = station_id.upper()
    if len(sid) == 4 and sid[0] in ('K', 'C', 'M', 'P'):
        sid3 = sid[1:]   # KDFW -> DFW
    else:
        sid3 = sid        # already 3-letter

    # ── Find station row ─────────────────────────────────────
    station_data = {}
    for line in lines[header_idx + 1:]:
        if not line.strip():
            continue
        parts = line.split()
        if not parts:
            continue
        row_id = parts[0].upper()
        if row_id in (sid, sid3):
            # Parse each column
            for col_idx, col_alt in enumerate(header_alts):
                if col_idx + 1 < len(parts):
                    decoded = _decode_fd(parts[col_idx + 1], col_alt)
                    if decoded:
                        station_data[col_alt] = decoded
            break

    if not station_data:
        return None

    # ── Interpolate to requested altitude ────────────────────
    available = sorted(station_data.keys())

    if alt_ft <= available[0]:
        return station_data[available[0]]
    if alt_ft >= available[-1]:
        return station_data[available[-1]]

    lo_alt = max(a for a in available if a <= alt_ft)
    hi_alt = min(a for a in available if a >= alt_ft)

    if lo_alt == hi_alt:
        return station_data[lo_alt]

    r1 = station_data[lo_alt]
    r2 = station_data[hi_alt]
    ratio = (alt_ft - lo_alt) / (hi_alt - lo_alt)

    # Vector interpolation for wind
    u1, v1 = _to_uv(r1["dir"], r1["speed_kt"])
    u2, v2 = _to_uv(r2["dir"], r2["speed_kt"])
    u = u1 + ratio * (u2 - u1)
    v = v1 + ratio * (v2 - v1)
    spd = round(math.sqrt(u*u + v*v))
    d   = round(math.degrees(math.atan2(-u, -v))) % 360 if spd >= 1 else 0
    temp = round(r1["temp_c"] + ratio * (r2["temp_c"] - r1["temp_c"]))

    return {
        "dir":      d,
        "speed_kt": spd,
        "temp_c":   temp,
        "variable": r1.get("variable", False),
    }


def _to_uv(direction: int, speed: int):
    r = math.radians(direction)
    return -speed * math.sin(r), -speed * math.cos(r)


def _decode_fd(code: str, alt_ft: int) -> dict | None:
    """
    Decode one FD column token.

    Formats seen in real data:
      "9900"        light & variable, no temp
      "0311+00"     dir=030 spd=11 temp=+00
      "3210-01"     dir=320 spd=10 temp=-01
      "296041"      dir=290 spd=60 temp=-41  (high winds: 6-char, temps always neg above FL240)
      "296351"      dir=290 spd=63 temp=-51
      "7803-21"     dir=780? -> high-wind encode: dir=(78-50)*10=280 spd=103 temp=-21
      "9900-09"     light & variable, temp=-09
    """
    code = code.strip()
    if not code or code == '////':
        return None

    # Light & variable
    if code[:4] == '9900':
        temp = 0
        if len(code) > 4:
            try:
                temp = int(code[4:])
                if alt_ft >= 24000:
                    temp = -abs(temp)
            except ValueError:
                pass
        return {"dir": 0, "speed_kt": 0, "temp_c": temp, "variable": True}

    # Try to parse with regex: DDSS[+/-]TT  or  DDSSTT (6 chars, high alt)
    # Also handles high-wind encode where DD >= 50 means speed += 100, dir -= 50
    m = re.match(r'^(\d{2})(\d{2})([+-]?\d+)?$', code)
    if not m:
        return None

    dd   = int(m.group(1))
    ss   = int(m.group(2))
    tt_s = m.group(3)

    # High-wind encoding: if dd > 50, direction = (dd-50)*10, speed += 100
    if dd > 50:
        dd = dd - 50
        ss = ss + 100

    direction = dd * 10
    speed     = ss

    # Temperature
    if tt_s is not None:
        try:
            temp = int(tt_s)
        except ValueError:
            temp = 0
    else:
        temp = 0

    # Above FL240 temps are always negative (no sign printed)
    if alt_ft >= 24000:
        temp = -abs(temp)

    return {"dir": direction, "speed_kt": speed, "temp_c": temp, "variable": False}


# ── Station database ─────────────────────────────────────────
# 3-letter FD station IDs with lat/lon — matches AWC table exactly

_FD_STATIONS = {
    "ABI": (32.41, -99.68), "ABQ": (35.04,-106.62), "ABR": (45.45, -98.42),
    "ACK": (41.25, -70.06), "ACY": (39.46, -74.57), "AGC": (40.35, -79.93),
    "ALB": (42.75, -73.80), "ALS": (37.43,-105.87), "AMA": (35.22,-101.71),
    "AST": (46.16,-123.88), "ATL": (33.64, -84.43), "AVP": (41.33, -75.73),
    "AXN": (45.87, -95.39), "BAM": (40.60,-116.87), "BAX": (44.43, -84.72),
    "BCE": (37.70,-112.15), "BDL": (41.94, -72.68), "BFF": (41.87,-103.60),
    "BGR": (44.81, -68.83), "BHM": (33.56, -86.75), "BIH": (37.37,-118.36),
    "BIL": (45.81,-108.54), "BLH": (33.62,-114.72), "BNA": (36.12, -86.68),
    "BOI": (43.56,-116.22), "BOS": (42.36, -71.01), "BRL": (40.78, -91.12),
    "BTR": (30.53, -91.15), "BUF": (42.93, -78.73), "BYI": (42.54,-113.77),
    "CAR": (46.87, -68.02), "CBE": (39.41, -78.76), "CEZ": (37.30,-108.63),
    "CHS": (32.90, -80.04), "CLE": (41.41, -81.85), "CLT": (35.21, -80.94),
    "CMH": (39.99, -82.89), "CNY": (38.75,-109.75), "COD": (44.52,-104.16),
    "CON": (43.20, -71.50), "COU": (38.82, -92.22), "CRP": (27.77, -97.51),
    "CVG": (39.05, -84.67), "CYS": (41.15,-104.81), "DAB": (29.18, -81.05),
    "DAL": (32.85, -96.85), "DEN": (39.85,-104.66), "DFW": (32.90, -97.04),
    "DLH": (46.84, -92.19), "DRT": (29.37,-100.92), "DSM": (41.53, -93.66),
    "DTW": (42.21, -83.35), "EKO": (40.82,-115.79), "ELP": (31.81,-106.38),
    "EVV": (38.04, -87.53), "EWR": (40.69, -74.17), "FAI": (64.81,-147.86),
    "FAR": (46.92, -96.81), "FAT": (36.78,-119.72), "FCA": (48.31,-114.26),
    "FLG": (35.13,-111.67), "FLL": (26.07, -80.15), "FMN": (36.74,-108.23),
    "FSD": (43.58, -96.74), "FSM": (35.34, -94.37), "GAG": (36.30, -99.78),
    "GEG": (47.62,-117.53), "GGG": (32.38, -94.71), "GJT": (39.12,-108.53),
    "GLD": (39.37,-101.70), "GRB": (44.48, -88.13), "GRR": (42.88, -85.52),
    "GSO": (36.10, -79.94), "GSP": (34.90, -82.22), "GTF": (47.48,-111.37),
    "HLN": (46.61,-111.98), "HOU": (29.65, -95.28), "HTS": (38.37, -82.56),
    "HUF": (39.45, -87.31), "HYS": (38.85, -99.27), "IAD": (38.94, -77.46),
    "ICT": (37.65, -97.43), "ILM": (34.27, -77.90), "IND": (39.71, -86.29),
    "INL": (48.57, -93.40), "JAC": (43.60,-110.74), "JAN": (32.31, -90.07),
    "JAX": (30.49, -81.69), "JFK": (40.63, -73.78), "JNU": (58.36,-134.58),
    "LAX": (33.94,-118.41), "LAS": (36.08,-115.15), "LBB": (33.66,-101.82),
    "LCH": (30.12, -93.22), "LIT": (34.73, -92.22), "LKV": (42.16,-120.40),
    "LNK": (40.85, -96.76), "LRD": (27.54, -99.46), "LSE": (43.88, -91.26),
    "MAF": (31.95,-102.21), "MCI": (39.29, -94.71), "MCO": (28.43, -81.31),
    "MDT": (40.19, -76.76), "MEM": (35.04, -89.98), "MFR": (42.37,-122.87),
    "MGM": (32.30, -86.39), "MIA": (25.79, -80.29), "MKE": (42.95, -87.90),
    "MLB": (28.10, -80.64), "MOB": (30.69, -88.24), "MSN": (43.14, -89.34),
    "MSO": (46.92,-114.09), "MSP": (44.88, -93.22), "MSY": (29.99, -90.26),
    "MTO": (39.48, -88.27), "OAK": (37.72,-122.22), "OKC": (35.39, -97.60),
    "OMA": (41.30, -95.90), "ONP": (44.58,-124.06), "ORD": (41.97, -87.91),
    "OTH": (43.42,-124.25), "PDX": (45.59,-122.60), "PHL": (39.87, -75.24),
    "PHX": (33.44,-112.01), "PIH": (42.91,-112.60), "PIT": (40.49, -80.23),
    "PNS": (30.47, -87.19), "PRC": (34.65,-112.42), "PSC": (46.26,-119.12),
    "PUB": (38.29,-104.50), "PVD": (41.72, -71.43), "RAP": (43.97,-103.06),
    "RDD": (40.51,-122.29), "RDU": (35.87, -78.79), "RIC": (37.50, -77.32),
    "RNO": (39.50,-119.78), "ROA": (37.32, -79.97), "ROW": (33.30,-104.53),
    "SAL": (38.84, -97.65), "SAN": (32.73,-117.19), "SAT": (29.53, -98.47),
    "SAV": (32.13, -81.20), "SBA": (34.43,-119.84), "SBN": (41.71, -86.32),
    "SEA": (47.45,-122.31), "SFO": (37.62,-122.38), "SGF": (37.24, -93.39),
    "SHV": (32.45, -93.83), "SLC": (40.78,-111.97), "SPS": (33.99, -98.49),
    "STL": (38.75, -90.37), "TLH": (30.40, -84.35), "TPA": (27.97, -82.53),
    "TUL": (36.20, -95.89), "TUS": (32.12,-110.94), "TWF": (42.48,-114.48),
    "VCT": (28.85, -96.93), "XMR": (28.47, -80.57), "YKM": (46.57,-120.54),
    # Alaska
    "ANC": (61.17,-150.02), "BET": (60.78,-161.84), "CDV": (60.49,-145.48),
    "OME": (64.51,-165.44), "SNP": (57.17,-170.22), "YAK": (59.51,-139.66),
}


def _nearest_fd_stations(lat: float, lon: float, n: int = 6) -> list[str]:
    def _dist(s):
        slat, slon = _FD_STATIONS[s]
        return math.hypot(lat - slat, lon - slon)
    return sorted(_FD_STATIONS.keys(), key=_dist)[:n]


# ── Public API ────────────────────────────────────────────────

def get_winds_at_point(lat: float, lon: float, cruise_fl: int) -> dict | None:
    alt_ft = cruise_fl * 100
    level  = _pick_level(cruise_fl)
    text   = _fetch_windtemp_text(level)
    if not text:
        return None

    for sid in _nearest_fd_stations(lat, lon, n=8):
        result = _parse_fd_table(text, sid, alt_ft)
        if result:
            result["station"] = sid
            return result
    return None


def headwind_component(wind_dir: int, wind_speed: int, course_deg: float) -> float:
    angle = math.radians(wind_dir - course_deg)
    return round(wind_speed * math.cos(angle), 1)


def crosswind_component(wind_dir: int, wind_speed: int, course_deg: float) -> float:
    angle = math.radians(wind_dir - course_deg)
    return round(wind_speed * math.sin(angle), 1)


def wind_corrected_groundspeed(tas_kt: float, wind_dir: int, wind_speed: int, course_deg: float) -> float:
    hw = headwind_component(wind_dir, wind_speed, course_deg)
    return max(1.0, tas_kt - hw)


def adjust_fuel_plan_for_wind(fp: dict, wind: dict, course_deg: float) -> dict:
    import copy
    fp2 = copy.deepcopy(fp)

    if not wind or wind.get("variable"):
        fp2.update({"wind_dir": 0, "wind_speed": 0, "wind_hw": 0.0,
                    "wind_gs": fp2["cruise_ktas"], "wind_adjusted": False,
                    "wind_station": wind.get("station", "N/A") if wind else "N/A"})
        return fp2

    hw  = headwind_component(wind["dir"], wind["speed_kt"], course_deg)
    gs  = wind_corrected_groundspeed(fp2["cruise_ktas"], wind["dir"], wind["speed_kt"], course_deg)

    new_cruise_time = fp2["cruise_dist_nm"] / gs if gs > 0 else fp2["cruise_time_hr"]
    burn            = fp2["cruise_burn_rate"]
    new_cruise_fuel = burn * new_cruise_time

    trip_fuel   = fp2["climb_fuel"] + new_cruise_fuel + fp2["descent_fuel"]
    contingency = trip_fuel * (fp2["poh"]["contingency_pct"] / 100)
    block_fuel  = fp2["taxi_fuel"] + trip_fuel + contingency + fp2["reserve"]
    total_time  = fp2["climb_time_hr"] + new_cruise_time + fp2["descent_time_hr"]

    fp2.update({
        "cruise_time_hr":  new_cruise_time,
        "cruise_fuel":     new_cruise_fuel,
        "trip_fuel":       trip_fuel,
        "contingency":     contingency,
        "block_fuel":      block_fuel,
        "total_time_hr":   total_time,
        "fuel_ok":         block_fuel <= fp2["usable_capacity"],
        "wind_dir":        wind["dir"],
        "wind_speed":      wind["speed_kt"],
        "wind_temp_c":     wind.get("temp_c", 0),
        "wind_hw":         hw,
        "wind_gs":         round(gs),
        "wind_station":    wind.get("station", "?"),
        "wind_adjusted":   True,
    })
    return fp2


def fetch_route_winds(dep, arr, waypoints, cruise_fl: int) -> list[dict]:
    dep_lat = float(dep.get("latitude_deg") or dep.get("lat") or 0)
    dep_lon = float(dep.get("longitude_deg") or dep.get("lon") or 0)
    arr_lat = float(arr.get("latitude_deg") or arr.get("lat") or 0)
    arr_lon = float(arr.get("longitude_deg") or arr.get("lon") or 0)

    points = [{"ident": dep.get("ident") or dep.get("icao_code", "DEP"),
               "lat": dep_lat, "lon": dep_lon}]

    if waypoints:
        step = max(1, len(waypoints) // 3)
        for i in range(0, len(waypoints), step):
            wp   = waypoints[i]
            wlat = float(wp.get("lat") or wp.get("latitude_deg") or 0)
            wlon = float(wp.get("lon") or wp.get("longitude_deg") or 0)
            if wlat and wlon:
                points.append({"ident": wp.get("ident", f"WP{i+1}"),
                                "lat": wlat, "lon": wlon})
    else:
        points.append({"ident": "MID",
                       "lat": (dep_lat + arr_lat) / 2,
                       "lon": (dep_lon + arr_lon) / 2})

    points.append({"ident": arr.get("ident") or arr.get("icao_code", "ARR"),
                   "lat": arr_lat, "lon": arr_lon})

    results = [None] * len(points)

    def _fetch(i, pt):
        w = get_winds_at_point(pt["lat"], pt["lon"], cruise_fl)
        results[i] = {**pt, "wind": w}

    threads = [threading.Thread(target=_fetch, args=(i, pt), daemon=True)
               for i, pt in enumerate(points)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=15)

    return [r for r in results if r is not None]


def course_deg(dep, arr) -> float:
    lat1 = math.radians(float(dep.get("latitude_deg") or dep.get("lat") or 0))
    lon1 = math.radians(float(dep.get("longitude_deg") or dep.get("lon") or 0))
    lat2 = math.radians(float(arr.get("latitude_deg") or arr.get("lat") or 0))
    lon2 = math.radians(float(arr.get("longitude_deg") or arr.get("lon") or 0))
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def wind_summary_line(route_winds: list[dict], course: float) -> str:
    # Pick the midpoint entry
    mid = None
    if len(route_winds) >= 3:
        mid = route_winds[len(route_winds) // 2]
    elif route_winds:
        mid = route_winds[-1]

    w = mid.get("wind") if mid else None
    if not w:
        return "🌬  Winds aloft: no data for this route"

    hw     = headwind_component(w["dir"], w["speed_kt"], course)
    temp   = w.get("temp_c", 0)
    stn    = w.get("station", "?")

    if w.get("variable"):
        wstr   = "VRB/LT"
        hw_str = ""
    else:
        wstr   = f"{w['dir']:03d}°/{w['speed_kt']}kt"
        hw_str = f"  {'HW' if hw >= 0 else 'TW'} {abs(hw):.0f}kt"

    return f"🌬  {wstr}{hw_str}  {temp:+d}°C  (stn: {stn})"