# ============================================================
# SimBrief Integration
# - Pre-fill dispatch URL builder
# - OFP fetch and parse
# ============================================================

import os
import requests
from urllib.parse import urlencode
from rich.panel import Panel
from rich.table import Table

SIMBRIEF_OFP_URL   = "https://www.simbrief.com/api/xml.fetcher.php"
SIMBRIEF_DISPATCH  = "https://dispatch.simbrief.com/options/custom"
REQUEST_TIMEOUT    = 10

# SimBrief fuel policy codes
FUEL_POLICIES = {
    "1": ("PAX",    "Standard PAX — recommended for airliners"),
    "2": ("MINPAX", "Minimum PAX — light load"),
    "3": ("GAF",    "GA Fixed — recommended for GA / turboprop"),
    "4": ("CUSTOM", "Custom — enter manually in SimBrief"),
}

# SimBrief unit options
UNIT_OPTIONS = {
    "1": "kgs",
    "2": "lbs",
}


def build_dispatch_url(
    dep_icao:    str,
    arr_icao:    str,
    alt_icao:    str | None,
    aircraft:    dict,
    simbrief_user: str,
    cruise_alt:  int | None = None,
    units:       str = "kgs",
) -> str:
    """
    Build a SimBrief Dispatch pre-fill URL.
    Opens in browser with all fields populated — user just clicks Generate.
    """
    params = {
        "orig":      dep_icao,
        "dest":      arr_icao,
        "type":      aircraft["simbrief_code"],
        "units":     units,
        "airline":   "",
        "fltnum":    _generate_flight_number(dep_icao, arr_icao),
        "selcal":    "",
        "dxname":    simbrief_user,
    }

    if alt_icao:
        params["altn"] = alt_icao

    if cruise_alt:
        params["fl"] = str(cruise_alt // 100)   # SimBrief expects FL e.g. 350
    else:
        params["fl"] = str(aircraft["cruise_alt"] // 100)

    return f"{SIMBRIEF_DISPATCH}?{urlencode(params)}"


def fetch_last_ofp(simbrief_user: str) -> dict | None:
    """
    Fetch the most recently generated OFP for a SimBrief user.
    Returns a simplified dict of key fields, or None on failure.
    """
    if not simbrief_user:
        return None

    try:
        resp = requests.get(
            SIMBRIEF_OFP_URL,
            params={"username": simbrief_user, "json": 1},
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "MSFS-FlightPlanner/1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid JSON response from SimBrief"}

    return _parse_ofp(data)


def _parse_ofp(data: dict) -> dict:
    """Extract key fields from SimBrief JSON OFP response."""
    try:
        origin  = data.get("origin",      {})
        dest    = data.get("destination", {})
        params  = data.get("params",      {})
        fuel    = data.get("fuel",        {})
        times   = data.get("times",       {})
        weights = data.get("weights",     {})
        general = data.get("general",     {})
        navlog  = data.get("navlog",      {})

        # Route waypoints summary
        fixes = navlog.get("fix", [])
        if isinstance(fixes, list) and len(fixes) > 0:
            waypoints = [f.get("ident", "") for f in fixes if f.get("ident")]
            route_str = " ".join(waypoints[:8])
            if len(waypoints) > 8:
                route_str += f" ... (+{len(waypoints)-8} fixes)"
        else:
            route_str = general.get("route", "N/A")

        return {
            "dep":              origin.get("icao_code",  "?"),
            "arr":              dest.get("icao_code",    "?"),
            "aircraft_icao":    general.get("icao_airline", ""),
            "aircraft_type":    params.get("type",       "?"),
            "flight_number":    general.get("icao_airline", "") + general.get("flight_number", ""),
            "cruise_fl":        params.get("cruise_altitude", "?"),
            "route":            route_str,
            "block_fuel_lbs":   fuel.get("plan_ramp",   "?"),
            "trip_fuel_lbs":    fuel.get("enroute_burn", "?"),
            "reserve_fuel_lbs": fuel.get("reserve",     "?"),
            "block_time":       times.get("est_block",  "?"),
            "est_zfw":          weights.get("est_zfw",  "?"),
            "units":            params.get("units",     "lbs"),
            "generated_at":     general.get("release",  "?"),
        }
    except Exception as e:
        return {"error": f"OFP parse error: {e}"}


def _generate_flight_number(dep: str, arr: str) -> str:
    """Generate a plausible GA-style flight number."""
    import random
    prefix = dep[:2].upper()
    number = random.randint(100, 999)
    return f"{prefix}{number}"


def prompt_simbrief_options(console) -> dict:
    """
    Ask the user for SimBrief dispatch preferences.
    Returns dict with units, show_last_ofp flag.
    """
    console.print("\n[bold cyan]SimBrief Options[/bold cyan]")

    # Units
    console.print("  Fuel units:")
    console.print("    [bold white]1[/bold white] — kg  (metric)")
    console.print("    [bold white]2[/bold white] — lbs (imperial)\n")
    while True:
        u = console.input("[bold yellow]Select units [1/2]: [/bold yellow]").strip()
        if u in UNIT_OPTIONS:
            units = UNIT_OPTIONS[u]
            break
        console.print("[red]Enter 1 or 2.[/red]")

    # Show last OFP?
    show_ofp = console.input(
        "\n[bold yellow]Fetch your last SimBrief OFP for reference? [y/N]: [/bold yellow]"
    ).strip().lower() in ("y", "yes")

    return {"units": units, "show_last_ofp": show_ofp}


def display_dispatch_link(console, url: str, dep: str, arr: str, alt: str | None):
    """Print the SimBrief dispatch URL in a prominent panel."""
    alt_str = f"  Alt  : [yellow]{alt}[/yellow]\n" if alt else ""
    console.print(Panel(
        f"[bold white]SimBrief Dispatch Pre-Fill[/bold white]\n\n"
        f"  Route: [cyan]{dep}[/cyan] → [cyan]{arr}[/cyan]\n"
        f"{alt_str}\n"
        f"[bold green]Open this URL in your browser:[/bold green]\n"
        f"[link={url}]{url}[/link]\n\n"
        f"[dim]All fields pre-populated — click [bold]Generate[/bold] to create your OFP.[/dim]",
        style="cyan",
        title="[bold cyan]✈  SimBrief[/bold cyan]",
    ))


def display_last_ofp(console, ofp: dict):
    """Display key fields from the last SimBrief OFP."""
    if not ofp:
        console.print("  [yellow]No OFP data available.[/yellow]")
        return

    if "error" in ofp:
        console.print(f"  [red]SimBrief error: {ofp['error']}[/red]")
        return

    units = ofp.get("units", "lbs").upper()

    table = Table(
        title="[bold cyan]Last Filed SimBrief OFP[/bold cyan]",
        show_header=False,
        box=None,
        padding=(0, 2),
    )
    table.add_column("Field", style="dim white",  width=18)
    table.add_column("Value", style="bold white", width=45)

    rows = [
        ("Route",        f"{ofp.get('dep','?')} → {ofp.get('arr','?')}"),
        ("Flight",       ofp.get("flight_number", "N/A")),
        ("Aircraft",     ofp.get("aircraft_type", "?")),
        ("Cruise FL",    f"FL{ofp.get('cruise_fl','?')}"),
        ("Route",        ofp.get("route", "N/A")),
        ("Block Fuel",   f"{ofp.get('block_fuel_lbs','?')} {units}"),
        ("Trip Fuel",    f"{ofp.get('trip_fuel_lbs','?')} {units}"),
        ("Reserve",      f"{ofp.get('reserve_fuel_lbs','?')} {units}"),
        ("Block Time",   ofp.get("block_time", "?")),
        ("Est. ZFW",     f"{ofp.get('est_zfw','?')} {units}"),
        ("Generated",    ofp.get("generated_at", "?")),
    ]

    for field, value in rows:
        table.add_row(field, str(value))

    console.print(table)