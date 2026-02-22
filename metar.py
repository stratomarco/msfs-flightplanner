import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Primary: Aviation Weather Center (NOAA) — no key needed ─
AWC_BASE   = "https://aviationweather.gov/api/data"
AWC_HEADERS = {"User-Agent": "MSFS-FlightPlanner/1.0"}

# ── Fallback: CheckWX — free key, global coverage ───────────
# Sign up free at https://www.checkwxapi.com (30 seconds, no CC)
# Then add CHECKWX_API_KEY=your_key to your .env file
CHECKWX_BASE = "https://api.checkwx.com"
CHECKWX_KEY  = os.getenv("CHECKWX_API_KEY", "")


# ── Helpers ──────────────────────────────────────────────────

def _safe_json(response):
    """Parse JSON safely — returns None on empty or invalid body."""
    try:
        if not response.text or not response.text.strip():
            return None
        return response.json()
    except (requests.exceptions.JSONDecodeError, ValueError):
        return None


def _normalize_checkwx(raw: dict) -> dict:
    """
    Map CheckWX response fields to AWC field names so the
    rest of the app works with one consistent schema.
    """
    if not raw:
        return {}
    return {
        "icaoId":    raw.get("icao", ""),
        "rawOb":     raw.get("raw_text", ""),
        "fltCat":    raw.get("flight_category", ""),
        "wdir":      raw.get("wind", {}).get("degrees", "---"),
        "wspd":      raw.get("wind", {}).get("speed_kts", "---"),
        "visib":     raw.get("visibility", {}).get("miles", "---"),
        "temp":      raw.get("temperature", {}).get("celsius", "---"),
        "altim":     raw.get("barometer", {}).get("hpa", "---"),
        # preserve raw for ceiling extraction
        "_source":   "checkwx",
    }


# ── Public API ───────────────────────────────────────────────

def get_metar(icao: str) -> dict | None:
    """
    Fetch latest METAR for a single airport.
    Tries AWC first, falls back to CheckWX if AWC returns empty.
    Returns None if both fail.
    """
    # 1 — Try AWC
    result = _awc_metar(icao)
    if result:
        return result

    # 2 — Fallback to CheckWX
    if CHECKWX_KEY:
        result = _checkwx_metar(icao)
        if result:
            return result

    return None


def get_taf(icao: str) -> dict | None:
    """Fetch TAF for a single airport."""
    try:
        r = requests.get(
            f"{AWC_BASE}/taf",
            params={"ids": icao, "format": "json"},
            headers=AWC_HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        data = _safe_json(r)
        if isinstance(data, list) and data:
            return data[0]
        return None
    except Exception:
        return None


def get_metar_batch(icao_list: list) -> list:
    """
    Fetch METARs for multiple airports in one call.
    Falls back to individual CheckWX calls for any missing.
    """
    if not icao_list:
        return []

    results = []
    found_icaos = set()

    # AWC batch
    try:
        r = requests.get(
            f"{AWC_BASE}/metar",
            params={"ids": ",".join(icao_list), "format": "json", "taf": "false"},
            headers=AWC_HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        data = _safe_json(r)
        if isinstance(data, list):
            results = data
            found_icaos = {m.get("icaoId", "").upper() for m in data}
    except Exception:
        pass

    # CheckWX fallback for any missing
    if CHECKWX_KEY:
        missing = [i for i in icao_list if i.upper() not in found_icaos]
        for icao in missing:
            m = _checkwx_metar(icao)
            if m:
                results.append(m)

    return results


def parse_flight_category(metar: dict) -> str:
    """
    Extract flight category from METAR dict.
    Handles both AWC (fltCat) and CheckWX (_source=checkwx) schemas.
    Returns one of: VFR, MVFR, IFR, LIFR, UNKN
    """
    if not metar:
        return "UNKN"

    # Direct field (AWC Sept 2025+ or CheckWX normalized)
    cat = metar.get("fltCat") or metar.get("flight_category", "")
    if cat and cat.upper() in ("VFR", "MVFR", "IFR", "LIFR"):
        return cat.upper()

    # Derive from raw METAR if field missing
    raw = metar.get("rawOb", "") or metar.get("raw_text", "")
    if not raw:
        return "UNKN"

    import re
    ceiling = None
    vis = None

    layers = re.findall(r'(BKN|OVC)(\d{3})', raw)
    if layers:
        ceiling = int(layers[0][1]) * 100

    vis_match = re.search(r'\s(\d+(?:/\d+)?)\s?SM', raw)
    if vis_match:
        try:
            vis_str = vis_match.group(1)
            if "/" in vis_str:
                num, den = vis_str.split("/")
                vis = float(num) / float(den)
            else:
                vis = float(vis_str)
        except ValueError:
            pass

    # Apply FAA flight category rules
    if ceiling is not None and ceiling < 500:
        return "LIFR"
    if vis is not None and vis < 1:
        return "LIFR"
    if ceiling is not None and ceiling < 1000:
        return "IFR"
    if vis is not None and vis < 3:
        return "IFR"
    if ceiling is not None and ceiling < 3000:
        return "MVFR"
    if vis is not None and vis < 5:
        return "MVFR"
    if ceiling is not None or vis is not None:
        return "VFR"

    return "UNKN"


def get_enroute_metars(dep_icao: str, arr_icao: str, db) -> list:
    """
    Find ~3 enroute METAR stations at 25%, 50%, 75% along the route.
    Searches medium/large airports near each interpolated point.
    """
    from geopy.distance import geodesic

    dep = db.get_airport(dep_icao)
    arr = db.get_airport(arr_icao)
    if not dep or not arr:
        return []

    dep_lat = float(dep["latitude_deg"])
    dep_lon = float(dep["longitude_deg"])
    arr_lat = float(arr["latitude_deg"])
    arr_lon = float(arr["longitude_deg"])

    waypoints = []
    for frac in (0.25, 0.50, 0.75):
        lat = dep_lat + (arr_lat - dep_lat) * frac
        lon = dep_lon + (arr_lon - dep_lon) * frac
        waypoints.append((lat, lon))

    stations = []
    seen = {dep_icao.upper(), arr_icao.upper()}

    for lat, lon in waypoints:
        # Find nearest medium/large airport within 100 NM of waypoint
        # We use a dummy ICAO lookup via coordinate proximity
        candidates = _nearest_reporting_station(db, lat, lon, seen)
        if candidates:
            stations.append(candidates)
            seen.add(candidates.upper())

    if not stations:
        return []

    metars = get_metar_batch(stations)
    return metars


# ── Private helpers ───────────────────────────────────────────

def _awc_metar(icao: str) -> dict | None:
    """Fetch a single METAR from AWC."""
    try:
        r = requests.get(
            f"{AWC_BASE}/metar",
            params={"ids": icao, "format": "json", "taf": "false"},
            headers=AWC_HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        data = _safe_json(r)
        if isinstance(data, list) and data:
            return data[0]
        return None
    except Exception:
        return None


def _checkwx_metar(icao: str) -> dict | None:
    """Fetch a single METAR from CheckWX and normalize to AWC schema."""
    if not CHECKWX_KEY:
        return None
    try:
        r = requests.get(
            f"{CHECKWX_BASE}/metar/{icao}/decoded",
            headers={
                "X-API-Key": CHECKWX_KEY,
                "Accept":    "application/json",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = _safe_json(r)
        if not data:
            return None
        results = data.get("data", [])
        if results:
            return _normalize_checkwx(results[0])
        return None
    except Exception:
        return None


def _nearest_reporting_station(db, lat: float, lon: float, exclude: set) -> str | None:
    """
    Find the nearest medium or large airport to (lat, lon)
    that is not in the exclude set. Returns ICAO or None.
    """
    import pandas as pd
    import numpy as np

    airports = db.airports
    subset = airports[
        airports["type"].isin(["medium_airport", "large_airport"]) &
        airports["icao_code"].notna() &
        ~airports["icao_code"].str.upper().isin(exclude)
    ].copy()

    if subset.empty:
        return None

    # Approximate distance in degrees (fast, good enough for selection)
    subset = subset.copy()
    subset["_dlat"] = subset["latitude_deg"].astype(float)  - lat
    subset["_dlon"] = subset["longitude_deg"].astype(float) - lon
    subset["_dist"] = np.sqrt(subset["_dlat"]**2 + subset["_dlon"]**2)

    nearest = subset.nsmallest(1, "_dist")
    if nearest.empty:
        return None

    return nearest.iloc[0]["icao_code"]