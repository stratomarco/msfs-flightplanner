# ============================================================
# notams.py — NOTAM fetcher for MSFS Flight Planner
#
# Source 1 (US airports): notams.aim.faa.gov public POST endpoint
#   — no auth required, official FAA data
# Source 2 (international): api.autorouter.aero free public API
#   — no auth required, Eurocontrol EAD data
#
# FAA official API (api.faa.gov) supported as optional upgrade:
#   pass client_id + client_secret if you have them
# ============================================================

import re
import json
import requests
from datetime import datetime, timezone

_HEADERS = {"User-Agent": "MSFS-FlightPlanner/1.0 (personal sim use)"}

# ── Source URLs ───────────────────────────────────────────────
_FAA_PUBLIC_URL  = "https://notams.aim.faa.gov/notamSearch/search"
_AUTOROUTER_URL  = "https://api.autorouter.aero/v1.0/notam"
_FAA_API_URL     = "https://external-api.faa.gov/notamapi/v1/notams"


# ── Category classification from Q-code ──────────────────────
_SUBJECT_MAP = {
    "MR": ("Runway",           1),
    "MT": ("Taxiway",          2),
    "MA": ("Movement Area",    2),
    "MK": ("Parking/Ramp",     3),
    "MX": ("Apron/Gate",       3),
    "LR": ("Rwy Lighting",     2),
    "LT": ("Taxiway Lights",   3),
    "LH": ("Threshold Lights", 2),
    "LB": ("Beacon",           3),
    "LS": ("Sequence Lights",  3),
    "LA": ("Apron Lighting",   4),
    "IC": ("ILS/CAT",          1),
    "IG": ("ILS Glide Slope",  1),
    "IL": ("ILS Localizer",    1),
    "IM": ("ILS Mid Marker",   2),
    "IO": ("ILS Outer Marker", 2),
    "IN": ("ILS Inner Marker", 2),
    "ND": ("NDB",              2),
    "VO": ("VOR",              2),
    "VD": ("VOR/DME",          2),
    "VT": ("TACAN",            2),
    "VA": ("VASI/PAPI",        2),
    "WA": ("Airspace",         1),
    "WU": ("Airspace Unserv.", 1),
    "RT": ("TFR",              1),
    "RR": ("Airspace Restric", 1),
    "PX": ("Approach Proc",    1),
    "PI": ("Instrument Apch",  1),
    "PR": ("RNAV/GPS Proc",    1),
    "PB": ("IFR Departure",    2),
    "AT": ("ATC",              2),
    "AF": ("ATC Freq",         2),
    "AG": ("ATIS",             3),
    "AR": ("ARFF",             3),
    "OB": ("Obstacle",         3),
    "OH": ("Hazard",           2),
    "FA": ("Airport General",  3),
    "FI": ("Airport Info",     3),
}

_PRIORITY_ICON = {1: "🔴", 2: "🟡", 3: "🔵", 4: "⚪"}


def _classify_from_qcode(qline: str) -> tuple[str, int]:
    """Extract subject code from Q) line and return (label, priority)."""
    # Q) FIR/QXXXX/... — grab the 4-char Q-code after the slash
    m = re.search(r'/Q([A-Z]{4})/', qline)
    if m:
        code = m.group(1)
        subj = code[1:3]
        return _SUBJECT_MAP.get(subj, ("General", 4))
    return ("General", 4)


def _classify_from_text(text: str) -> tuple[str, int]:
    """Fallback: guess category from NOTAM text keywords."""
    t = text.upper()
    for kw, cat, pri in [
        ("RWY", "Runway", 1), ("RUNWAY", "Runway", 1),
        ("CLSD", "Closure", 1), ("CLOSED", "Closure", 1),
        ("ILS", "ILS/CAT", 1), ("LOC", "ILS Localizer", 1),
        ("GS ", "ILS Glide Slope", 1),
        ("TFR", "TFR", 1), ("TEMPORARY FLIGHT", "TFR", 1),
        ("VOR", "VOR", 2), ("NDB", "NDB", 2), ("TACAN", "TACAN", 2),
        ("TWY", "Taxiway", 2), ("TAXIWAY", "Taxiway", 2),
        ("PAPI", "VASI/PAPI", 2), ("VASI", "VASI/PAPI", 2),
        ("APCH", "Approach Proc", 1), ("APPROACH", "Approach Proc", 1),
        ("ATIS", "ATIS", 3), ("LIGHT", "Lighting", 3),
        ("OBST", "Obstacle", 3), ("CRANE", "Obstacle", 3),
    ]:
        if kw in t:
            return cat, pri
    return "General", 4


def _fmt_time(ts: str) -> str:
    """Format timestamp string to short readable form."""
    if not ts:
        return "?"
    # Handle YYMMDDHHMM format (FAA domestic)
    if re.match(r'^\d{10}$', ts):
        try:
            dt = datetime.strptime(ts, "%y%m%d%H%M").replace(tzinfo=timezone.utc)
            return dt.strftime("%d%b %H%MZ")
        except ValueError:
            pass
    # Handle ISO format
    try:
        s = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        return dt.strftime("%d%b %H%MZ")
    except Exception:
        return ts[:16]


# ── FAA public search (no auth) ───────────────────────────────

def _fetch_faa_public(icao: str) -> list[dict]:
    """
    Fetch NOTAMs from notams.aim.faa.gov public POST endpoint.
    No authentication required — same data as the FAA NOTAM Search website.
    """
    # Strip leading K for domestic airports if needed (site uses 4-letter)
    icao4 = icao.upper()
    if len(icao4) == 3:
        icao4 = "K" + icao4

    payload = {
        "retrieveLocId":       icao4,
        "notamType":           "N",
        "radiusWithCenterIC":  "N",
        "radiusInNM":          "10",
        "latDegrees":          "0",
        "latMinutes":          "0",
        "latSeconds":          "0",
        "longDegrees":         "0",
        "longMinutes":         "0",
        "longSeconds":         "0",
        "latitudeDirection":   "N",
        "longitudeDirection":  "W",
        "sortColumns":         "5 false",
        "sortDirection":       "true",
        "pageSize":            "50",
        "pageNumber":          "0",
        "systemType":          "DOMAIN",
        "actionType":          "notamRetrievalByICAOs",
    }

    try:
        resp = requests.post(
            _FAA_PUBLIC_URL,
            data=payload,
            headers={**_HEADERS,
                     "Content-Type": "application/x-www-form-urlencoded",
                     "Accept":       "application/json"},
            timeout=12,
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        items = data.get("notamList") or []
        results = []
        for item in items:
            # FAA public search returns notamNumber, icaoId, notamText fields
            text = (item.get("traditionalMessageFrom4thWord")
                    or item.get("notamText")
                    or item.get("icaoMessage")
                    or "").strip()
            if not text:
                continue

            # Try to find Q-line for classification
            full = item.get("icaoMessage") or item.get("notamText") or ""
            qmatch = re.search(r'Q\)\s*\S+/Q\w+/', full)
            if qmatch:
                cat, pri = _classify_from_qcode(qmatch.group())
            else:
                cat, pri = _classify_from_text(text)

            results.append({
                "id":       item.get("notamNumber") or item.get("icaoId") or "?",
                "location": icao4,
                "category": cat,
                "priority": pri,
                "effective": (item.get("startDate") or item.get("effectiveStartDate") or ""),
                "expires":   (item.get("endDate")   or item.get("effectiveEndDate")   or ""),
                "text":      text,
            })
        return results

    except Exception:
        return []


# ── Autorouter (free, international) ─────────────────────────

def _fetch_autorouter(icao: str) -> list[dict]:
    """
    Fetch NOTAMs from api.autorouter.aero — free, no auth, Eurocontrol data.
    Good fallback for non-US airports or when FAA is unavailable.
    """
    try:
        resp = requests.get(
            _AUTOROUTER_URL,
            params={"itemas": json.dumps([icao.upper()]),
                    "offset": 0, "limit": 50},
            headers=_HEADERS,
            timeout=12,
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        rows = data.get("rows") or []
        results = []
        for row in rows:
            text = row.get("message") or row.get("raw") or ""
            if not text:
                continue
            qmatch = re.search(r'Q\)\s*\S+/Q\w+/', text)
            cat, pri = (_classify_from_qcode(qmatch.group())
                        if qmatch else _classify_from_text(text))
            results.append({
                "id":        row.get("id") or "?",
                "location":  icao.upper(),
                "category":  cat,
                "priority":  pri,
                "effective": row.get("startvalidity") or "",
                "expires":   row.get("endvalidity")   or "",
                "text":      text.strip(),
            })
        return results

    except Exception:
        return []


# ── FAA official API (optional, requires key) ─────────────────

def _fetch_faa_api(icao: str, client_id: str, client_secret: str) -> list[dict]:
    """Fetch from official FAA API if credentials provided."""
    try:
        resp = requests.get(
            _FAA_API_URL,
            params={"icaoLocation": icao.upper(), "pageSize": 50, "pageNum": 1},
            auth=(client_id, client_secret),
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code not in (200, 204):
            return []

        items = resp.json().get("items") or []
        results = []
        for item in items:
            core = item.get("coreNOTAMData", {})
            notam = core.get("notam", item)
            text = (notam.get("traditionalMessageFrom4thWord")
                    or notam.get("traditionalMessage") or "").strip()
            if not text:
                continue
            q = notam.get("selectionCode", "")
            cat, pri = _classify_from_qcode(f"/Q{q}/") if q else _classify_from_text(text)
            results.append({
                "id":        notam.get("id") or "?",
                "location":  icao.upper(),
                "category":  cat,
                "priority":  pri,
                "effective": notam.get("effectiveStart") or "",
                "expires":   notam.get("effectiveEnd")   or "",
                "text":      text,
            })
        return results

    except Exception:
        return []


# ── Public entry points ───────────────────────────────────────

def fetch_notams(icao: str, client_id: str = "", client_secret: str = "") -> list[dict]:
    """
    Fetch NOTAMs for one airport. Uses the best available source:
    1. Official FAA API if credentials provided
    2. FAA public search (no auth)
    3. Autorouter fallback
    """
    results = []

    # Try official API first if we have keys
    if client_id and client_secret:
        results = _fetch_faa_api(icao, client_id, client_secret)

    # Fall back to public FAA search
    if not results:
        results = _fetch_faa_public(icao)

    # Fall back to autorouter
    if not results:
        results = _fetch_autorouter(icao)

    if not results:
        return [{"id": "NONE", "location": icao, "category": "Info", "priority": 5,
                 "effective": "", "expires": "",
                 "text": f"No active NOTAMs found for {icao}, or data unavailable."}]

    # Sort: priority first, then effective date
    results.sort(key=lambda x: (x["priority"], x.get("effective", "")))
    return results


def fetch_route_notams(dep_icao: str, arr_icao: str,
                       client_id: str = "", client_secret: str = "") -> dict:
    """Fetch NOTAMs for dep and arr in parallel. Returns {icao: [notams]}."""
    import threading
    out = {}

    def _fetch(icao):
        if icao:
            out[icao] = fetch_notams(icao, client_id, client_secret)

    icaos = list({dep_icao, arr_icao} - {""})
    threads = [threading.Thread(target=_fetch, args=(ic,), daemon=True) for ic in icaos]
    for t in threads: t.start()
    for t in threads: t.join(timeout=18)

    return out


# ── Popup formatter ───────────────────────────────────────────

def format_notams_text(notams_by_airport: dict) -> str:
    lines = []

    for icao, notams in notams_by_airport.items():
        lines += [f"{'═'*64}", f"  NOTAMs — {icao}", f"{'═'*64}"]

        if not notams:
            lines += ["  No active NOTAMs.", ""]
            continue

        critical  = [n for n in notams if n["priority"] == 1]
        important = [n for n in notams if n["priority"] == 2]
        advisory  = [n for n in notams if n["priority"] >= 3]

        parts = []
        if critical:  parts.append(f"🔴 {len(critical)} critical")
        if important: parts.append(f"🟡 {len(important)} important")
        if advisory:  parts.append(f"🔵 {len(advisory)} advisory")
        lines += [f"  {' | '.join(parts)} — {len(notams)} total", ""]

        current_cat = None
        for n in notams:
            if n["category"] != current_cat:
                current_cat = n["category"]
                lines.append(f"  ── {current_cat} {'─'*(46-len(current_cat))}")

            icon = _PRIORITY_ICON.get(n["priority"], "⚪")
            eff  = _fmt_time(n["effective"]) if n["effective"] else "now"
            exp  = _fmt_time(n["expires"])   if n["expires"]   else "PERM"
            lines.append(f"  {icon} [{n['id']}]  {eff} → {exp}")

            # Word-wrap at 60 chars
            words    = n["text"].split()
            line_buf = "      "
            for word in words:
                if len(line_buf) + len(word) + 1 > 64:
                    lines.append(line_buf)
                    line_buf = "      " + word
                else:
                    line_buf += (" " if line_buf.strip() else "") + word
            if line_buf.strip():
                lines.append(line_buf)
            lines.append("")

    return "\n".join(lines)