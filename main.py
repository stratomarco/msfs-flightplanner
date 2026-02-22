import os
import re
import webbrowser
from dotenv import load_dotenv
from geopy.distance import geodesic
from airport_db import AirportDB
from metar import get_metar, parse_flight_category, get_enroute_metars
from aircraft import select_aircraft, estimate_flight_time
from destination import pick_destination
from alternate import alternate_required, find_alternate, describe_alternate_requirement
from simbrief import (
    build_dispatch_url, fetch_last_ofp,
    prompt_simbrief_options, display_dispatch_link, display_last_ofp
)
from navigraph import display_key_charts
from flightplan import prompt_export, OUTPUT_DIR
from logbook import prompt_log_flight
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

db = AirportDB("data/airports.csv", "data/runways.csv")

CATEGORY_COLORS = {
    "VFR":  "bold green",
    "MVFR": "bold yellow",
    "IFR":  "bold red",
    "LIFR": "bold magenta",
    "UNKN": "white",
}


def print_metar(icao: str):
    """Fetch and pretty-print a METAR. Returns the raw metar dict."""
    metar = get_metar(icao)
    if not metar:
        console.print(f"    [yellow]{icao}:[/yellow] No METAR available")
        return None
    cat = parse_flight_category(metar)
    color = CATEGORY_COLORS.get(cat, "white")
    console.print(f"    [cyan]{icao}[/cyan] | [{color}]{cat}[/{color}]")
    console.print(f"           {metar.get('rawOb', 'N/A')}")
    console.print(
        f"           Wind: {metar.get('wdir', '---')}° @ {metar.get('wspd', '---')}kt | "
        f"Vis: {metar.get('visib', '---')}SM | "
        f"Temp: {metar.get('temp', '---')}°C"
    )
    return metar


def _recommend_flight_rules(dep_metar, arr_metar):
    """Print weather-based recommendation. Returns worst flight category."""
    categories = []
    for m in [dep_metar, arr_metar]:
        if m:
            cat = parse_flight_category(m)
            if cat:
                categories.append(cat)

    if not categories:
        console.print("  [yellow]Unable to determine — no METAR data available.[/yellow]")
        return "VFR"

    order = ["VFR", "MVFR", "IFR", "LIFR"]
    worst = max(categories, key=lambda c: order.index(c) if c in order else 0)

    if worst == "VFR":
        console.print(
            "  [bold green]✓ VFR CONDITIONS[/bold green] — "
            "Visual flight rules applicable at both ends."
        )
    elif worst == "MVFR":
        console.print(
            "  [bold yellow]⚠  MARGINAL VFR[/bold yellow] — "
            "IFR recommended. Ceilings or vis below VFR minimums."
        )
    elif worst in ("IFR", "LIFR"):
        console.print(
            "  [bold red]✗ IFR CONDITIONS[/bold red] — "
            "Below VFR minimums. Instrument flight rules required."
        )
    return worst

def run():
    console.print(Panel(
        "[bold white]MSFS 2024 Flight Planner[/bold white]\n"
        "[dim]Full Dispatch: Weather · Alternate · SimBrief · Navigraph · Logbook[/dim]",
        style="blue"
    ))

    # ── Step 1: Select aircraft ──────────────────────────────
    aircraft = select_aircraft(console)

    # ── Step 2: Pick destination ─────────────────────────────
    dest = pick_destination(console, db, aircraft)
    if dest is None:
        console.print("[yellow]No destination selected. Exiting.[/yellow]")
        return

    # ── Step 3: Confirm departure ────────────────────────────
    while True:
        dep_icao = console.input(
            "\n[bold yellow]Enter departure ICAO (e.g. KDFW): [/bold yellow]"
        ).strip().upper()
        dep = db.get_airport(dep_icao)
        if dep:
            break
        console.print(f"[red]Airport {dep_icao!r} not found. Try again.[/red]")

    arr = db.get_airport(dest["icao_code"])
    if not arr:
        console.print(f"[red]Could not resolve arrival airport {dest['icao_code']!r}.[/red]")
        return

    # ── Step 4: Distance + time ──────────────────────────────
    dist_nm = geodesic(
        (dep["latitude_deg"], dep["longitude_deg"]),
        (arr["latitude_deg"], arr["longitude_deg"])
    ).nautical

    ftime = estimate_flight_time(dist_nm, aircraft)

    console.print(Panel(
        f"[bold cyan]{dep['icao_code']}[/bold cyan]  →  "
        f"[bold cyan]{arr['icao_code']}[/bold cyan]\n"
        f"{dep['name']}\n→ {arr['name']}\n\n"
        f"Distance : [green]{dist_nm:.0f} NM[/green]\n"
        f"Est. time: [magenta]{ftime}[/magenta]\n"
        f"Aircraft : [cyan]{aircraft['label']}[/cyan]  "
        f"[dim]({aircraft['developer']})[/dim]",
        title="[bold white]Route[/bold white]",
        style="blue"
    ))

    # ── Step 5: Weather briefing ─────────────────────────────
    console.print("\n[bold underline]WEATHER BRIEFING[/bold underline]")

    console.print(f"  [bold]Departure  ({dep['icao_code']}):[/bold]")
    dep_metar = print_metar(dep['icao_code'])

    console.print(f"\n  [bold]Arrival    ({arr['icao_code']}):[/bold]")
    arr_metar = print_metar(arr['icao_code'])

    console.print("\n  [bold]Enroute:[/bold]")
    try:
        enroute = get_enroute_metars(dep['icao_code'], arr['icao_code'], db)
        if enroute:
            for m in enroute:
                cat = parse_flight_category(m)
                color = CATEGORY_COLORS.get(cat, "white")
                console.print(
                    f"    [cyan]{m.get('icaoId', '?')}[/cyan] | "
                    f"[{color}]{cat}[/{color}] | "
                    f"{m.get('rawOb', 'N/A')}"
                )
        else:
            console.print("    [dim]No enroute METAR stations found.[/dim]")
    except Exception as e:
        console.print(f"    [red]Enroute fetch failed: {e}[/red]")

# ── Step 6: Flight rules selection ──────────────────────
    console.print("\n[bold underline]FLIGHT RULES[/bold underline]")

    # Show weather-based recommendation first
    worst_cat = _recommend_flight_rules(dep_metar, arr_metar)
    wx_suggested = "IFR" if worst_cat in ("IFR", "LIFR", "MVFR") else "VFR"

    # Let the pilot decide
    console.print(
        f"\n  Weather suggests: [bold]{'[red]IFR' if wx_suggested == 'IFR' else '[green]VFR'}[/bold]\n"
        f"  [dim](You can file IFR in VMC for currency, airways, or preference)[/dim]\n"
    )
    console.print("    [bold white]1[/bold white] — VFR")
    console.print("    [bold white]2[/bold white] — IFR\n")

    while True:
        fr_choice = console.input(
            f"[bold yellow]Select flight rules [1=VFR / 2=IFR] "
            f"(Enter for suggested {wx_suggested}): [/bold yellow]"
        ).strip()

        if fr_choice == "" :
            pln_rules = wx_suggested
            break
        elif fr_choice == "1":
            pln_rules = "VFR"
            break
        elif fr_choice == "2":
            pln_rules = "IFR"
            break
        console.print("[red]Enter 1 for VFR, 2 for IFR, or just press Enter.[/red]")

    # Warn if filing VFR in IFR conditions
    if pln_rules == "VFR" and worst_cat in ("IFR", "LIFR"):
        console.print(
            "  [bold red]⚠  WARNING:[/bold red] Filing VFR in IFR conditions. "
            "Ensure you have visual separation and legal minimums."
        )
    elif pln_rules == "IFR" and worst_cat == "VFR":
        console.print(
            "  [bold green]✓ IFR in VMC[/bold green] — "
            "Good practice for currency and controlled airspace."
        )

    console.print(f"  [bold]Filed:[/bold] [bold cyan]{pln_rules}[/bold cyan]")
    # ── Step 7: Alternate airport ────────────────────────────
    console.print("\n[bold underline]ALTERNATE[/bold underline]")
    describe_alternate_requirement(console, arr_metar)

    alt_airport = None
    if alternate_required(arr_metar):
        alt_airport = find_alternate(
            console, db, arr['icao_code'], arr_metar, aircraft
        )

    # ── Step 8: SimBrief ─────────────────────────────────────
    simbrief_user = os.getenv("SIMBRIEF_USERNAME", "").strip()
    dispatch_url  = None

    console.print("\n[bold underline]SIMBRIEF DISPATCH[/bold underline]")

    if not simbrief_user:
        console.print(
            "  [yellow]⚠  SIMBRIEF_USERNAME not set in .env — skipped.[/yellow]"
        )
    else:
        sb_opts = prompt_simbrief_options(console)

        dispatch_url = build_dispatch_url(
            dep_icao      = dep['icao_code'],
            arr_icao      = arr['icao_code'],
            alt_icao      = alt_airport['icao_code'] if alt_airport else None,
            aircraft      = aircraft,
            simbrief_user = simbrief_user,
            units         = sb_opts["units"],
        )

        display_dispatch_link(
            console,
            dispatch_url,
            dep['icao_code'],
            arr['icao_code'],
            alt_airport['icao_code'] if alt_airport else None,
        )

        if sb_opts["show_last_ofp"]:
            console.print("\n[dim]Fetching your last SimBrief OFP...[/dim]")
            ofp = fetch_last_ofp(simbrief_user)
            display_last_ofp(console, ofp)

    # ── Step 9: Navigraph Charts ─────────────────────────────
    console.print("\n[bold underline]NAVIGRAPH CHARTS[/bold underline]")
    display_key_charts(
        console,
        dep['icao_code'],
        arr['icao_code'],
        alt_airport['icao_code'] if alt_airport else None,
    )

    # ── Step 10: Launch SimBrief in browser ──────────────────
    if dispatch_url:
        launch = console.input(
            "\n[bold yellow]Open SimBrief Dispatch in browser now? [Y/n]: [/bold yellow]"
        ).strip().lower()
        if launch in ("", "y", "yes"):
            webbrowser.open(dispatch_url)
            console.print("  [green]✓ Opened in default browser.[/green]")

    # ── Step 10b: Export .pln ────────────────────────────────
    pln_file = prompt_export(
        console      = console,
        dep          = dep,
        arr          = arr,
        aircraft     = aircraft,
        alt_airport  = alt_airport,
        flight_rules = pln_rules,
        cruise_alt   = aircraft["cruise_alt"],
    )

    # ── Step 10c: Log the flight ─────────────────────────────
    time_match = re.match(r'(\d+)h\s*(\d+)m', ftime)
    if time_match:
        block_hrs = int(time_match.group(1)) + int(time_match.group(2)) / 60
    else:
        block_hrs = dist_nm / aircraft["cruise_kts"]

    prompt_log_flight(
        console        = console,
        dep            = dep,
        arr            = arr,
        aircraft       = aircraft,
        block_time_hrs = block_hrs,
        flight_rules   = pln_rules,
        dist_nm        = dist_nm,
        alt_airport    = alt_airport,
        dep_metar      = dep_metar,
        arr_metar      = arr_metar,
    )

    # ── Step 11: Final dispatch summary ─────────────────────
    console.print("")

    alt_line = (
        f"Alternate  : [yellow]{alt_airport['icao_code']}[/yellow] — "
        f"{alt_airport['name']}  "
        f"[dim]({alt_airport['dist_nm']:.0f} NM from destination)[/dim]"
        if alt_airport
        else "[dim]Alternate  : None filed[/dim]"
    )

    sb_line = (
        f"SimBrief   : [link={dispatch_url}][cyan]Pre-fill URL ready[/cyan][/link]"
        if dispatch_url
        else "[dim]SimBrief   : Not configured[/dim]"
    )

    pln_line = (
        f"Flight Plan: [green]{os.path.basename(pln_file)}[/green]  "
        f"[dim](saved to {OUTPUT_DIR}/)[/dim]"
        if pln_file
        else "[dim]Flight Plan: Not exported[/dim]"
    )

    console.print(Panel(
        f"[bold cyan]{dep['icao_code']}[/bold cyan]  →  "
        f"[bold cyan]{arr['icao_code']}[/bold cyan]\n"
        f"Aircraft   : [cyan]{aircraft['label']}[/cyan]\n"
        f"Distance   : [green]{dist_nm:.0f} NM[/green]   "
        f"Est. time  : [magenta]{ftime}[/magenta]\n"
        f"{alt_line}\n"
        f"{sb_line}\n"
        f"{pln_line}",
        title="[bold white]✈  Dispatch Summary[/bold white]",
        style="blue",
    ))

    console.print(Panel(
        "[bold green]✓ Full Dispatch Complete[/bold green]\n"
        "[dim]Next: GUI — proper desktop window[/dim]",
        style="green"
    ))


if __name__ == "__main__":
    run()