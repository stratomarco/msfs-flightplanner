# ============================================================
# MSFS 2024 Flight Plan Exporter (.pln)
# XML format compatible with MSFS 2024 World Map
# ============================================================

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone

# Default MSFS 2024 Community folder locations
MSFS_PLN_PATHS = [
    os.path.expanduser(r"~\AppData\Roaming\Microsoft Flight Simulator\Plans"),
    os.path.expanduser(r"~\AppData\Local\Packages\Microsoft.FlightSimulator_8wekyb3d8bbwe\LocalState\Plans"),
]

OUTPUT_DIR = "output_plans"


def export_pln(
    dep:        dict,
    arr:        dict,
    aircraft:   dict,
    alt_airport: dict | None = None,
    flight_rules: str = "IFR",
    cruise_alt:  int | None = None,
) -> str:
    """
    Generate an MSFS 2024 .pln flight plan file.
    Returns the path of the saved file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dep_icao = dep["icao_code"]
    arr_icao = arr["icao_code"]
    alt_icao = alt_airport["icao_code"] if alt_airport else None
    fl        = cruise_alt or aircraft["cruise_alt"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename  = f"{dep_icao}_{arr_icao}_{timestamp}.pln"
    filepath  = os.path.join(OUTPUT_DIR, filename)

    root = ET.Element("SimBase.Document", {
        "Type":    "AceXML",
        "version": "1,0",
    })

    # ── Descr ────────────────────────────────────────────────
    descr = ET.SubElement(root, "Descr")
    descr.text = "AceXML Document"

    # ── FlightPlan.FlightPlan ────────────────────────────────
    fp = ET.SubElement(root, "FlightPlan.FlightPlan")

    _elem(fp, "Title",          f"{dep_icao} to {arr_icao}")
    _elem(fp, "FPType",         flight_rules)
    _elem(fp, "RouteType",      "HighAlt" if fl >= 18000 else "LowAlt")
    _elem(fp, "CruisingAlt",    str(fl))
    _elem(fp, "DepartureID",    dep_icao)
    _elem(fp, "DepartureLLA",   _lla(dep))
    _elem(fp, "DestinationID",  arr_icao)
    _elem(fp, "DestinationLLA", _lla(arr))
    _elem(fp, "Descr",          f"{dep_icao} — {arr_icao} | {aircraft['label']}")
    _elem(fp, "DeparturePosition", "")
    _elem(fp, "DepartureName",  dep.get("name", dep_icao))
    _elem(fp, "DestinationName",arr.get("name", arr_icao))
    _elem(fp, "AppVersion",     "11,1,282174,0")

    # ── Waypoints ────────────────────────────────────────────
    # Departure
    _waypoint(fp, dep,
              wp_type="Airport",
              id_=dep_icao,
              is_origin=True)

    # Alternate as an enroute waypoint if present
    # (MSFS doesn't have a native alternate field — we add it
    #  as the final waypoint after destination with a comment)
    if alt_airport:
        _waypoint(fp, alt_airport,
                  wp_type="Airport",
                  id_=alt_icao,
                  is_origin=False,
                  comment=f"ALTERNATE: {alt_icao}")

    # Destination
    _waypoint(fp, arr,
              wp_type="Airport",
              id_=arr_icao,
              is_origin=False,
              is_destination=True)

    # ── Pretty-print XML ─────────────────────────────────────
    xml_str = _prettify(root)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_str)

    return filepath


def copy_to_msfs(filepath: str, console) -> bool:
    """
    Attempt to copy the .pln file to the MSFS Plans folder.
    Returns True if successful.
    """
    for plans_dir in MSFS_PLN_PATHS:
        if os.path.isdir(plans_dir):
            import shutil
            dest = os.path.join(plans_dir, os.path.basename(filepath))
            try:
                shutil.copy2(filepath, dest)
                console.print(
                    f"  [green]✓ Copied to MSFS Plans folder:[/green]\n"
                    f"    [dim]{dest}[/dim]"
                )
                return True
            except Exception as e:
                console.print(f"  [red]Copy failed: {e}[/red]")
    return False


def prompt_export(console, dep, arr, aircraft, alt_airport, flight_rules, cruise_alt) -> str | None:
    """
    Ask user if they want to export a .pln and optionally copy to MSFS.
    Returns filepath or None.
    """
    console.print("\n[bold underline]FLIGHT PLAN EXPORT[/bold underline]")

    export = console.input(
        "[bold yellow]Export .pln flight plan for MSFS? [Y/n]: [/bold yellow]"
    ).strip().lower()

    if export not in ("", "y", "yes"):
        console.print("  [dim]Export skipped.[/dim]")
        return None

    filepath = export_pln(
        dep          = dep,
        arr          = arr,
        aircraft     = aircraft,
        alt_airport  = alt_airport,
        flight_rules = flight_rules,
        cruise_alt   = cruise_alt,
    )

    console.print(
        f"  [green]✓ Flight plan saved:[/green] [cyan]{filepath}[/cyan]"
    )

    # Try auto-copy to MSFS
    copied = copy_to_msfs(filepath, console)
    if not copied:
        console.print(
            "  [yellow]MSFS Plans folder not found — copy manually to:[/yellow]\n"
            "  [dim]%APPDATA%\\Microsoft Flight Simulator\\Plans\\[/dim]\n"
            "  [dim]Then load it from the World Map → Load/Save → My Flight Plans[/dim]"
        )

    return filepath


# ── XML helpers ───────────────────────────────────────────────

def _elem(parent, tag: str, text: str):
    e = ET.SubElement(parent, tag)
    e.text = text
    return e


def _lla(airport: dict) -> str:
    """Format lat/lon/alt as MSFS LLA string: N47° 27.72',E008° 33.40',+0455.00"""
    lat  = float(airport["latitude_deg"])
    lon  = float(airport["longitude_deg"])
    elev = float(airport.get("elevation_ft") or 0)

    lat_hem = "N" if lat >= 0 else "S"
    lon_hem = "E" if lon >= 0 else "W"
    lat_abs = abs(lat)
    lon_abs = abs(lon)

    lat_deg = int(lat_abs)
    lat_min = (lat_abs - lat_deg) * 60
    lon_deg = int(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60

    return (
        f"{lat_hem}{lat_deg}° {lat_min:.2f}',"
        f"{lon_hem}{lon_deg}° {lon_min:.2f}',"
        f"+{elev:.2f}"
    )


def _waypoint(
    parent,
    airport:        dict,
    wp_type:        str  = "Airport",
    id_:            str  = "",
    is_origin:      bool = False,
    is_destination: bool = False,
    comment:        str  = "",
):
    wp = ET.SubElement(parent, "ATCWaypoint", {"id": id_})
    _elem(wp, "ATCWaypointType", wp_type)
    _elem(wp, "WorldPosition",   _lla(airport))
    _elem(wp, "SpeedMaxFP",      "-1")

    if comment:
        _elem(wp, "ATCComment", comment)

    icao = ET.SubElement(wp, "ICAO")
    _elem(icao, "ICAOIdent",   id_)
    _elem(icao, "ICAORegion",  _icao_region(airport))


def _icao_region(airport: dict) -> str:
    """Map iso_country to ICAO region prefix for the .pln file."""
    country_map = {
        "US": "K",  "CA": "C",  "GB": "EG", "DE": "ED",
        "FR": "LF", "ES": "LE", "IT": "LI", "NL": "EH",
        "AU": "Y",  "NZ": "NZ", "BR": "SB", "AR": "SA",
        "MX": "MM", "JP": "RJ", "CN": "Z",  "IN": "VI",
    }
    country = airport.get("iso_country", "")
    return country_map.get(country, country[:2].upper())


def _prettify(element) -> str:
    """Return a pretty-printed XML string with declaration."""
    raw = ET.tostring(element, encoding="unicode")
    parsed = minidom.parseString(raw)
    pretty = parsed.toprettyxml(indent="    ", encoding=None)
    # minidom adds its own declaration — replace with clean one
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    return "\n".join(lines)