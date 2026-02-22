# ============================================================
# Destination Picker
# Time-based, random, and "surprise me" destination selection
# ============================================================

import random
from rich.table import Table
from rich.panel import Panel


def pick_destination(console, db, aircraft: dict, mode: str = None) -> dict | None:
    """
    Main entry point for destination selection.
    mode: 'time' | 'random' | None (will prompt)
    Returns selected airport dict or None if cancelled.
    """
    if mode is None:
        mode = _prompt_mode(console)

    if mode == "time":
        return _time_based_picker(console, db, aircraft)
    elif mode == "random":
        return _random_picker(console, db, aircraft)
    return None


def _prompt_mode(console) -> str:
    console.print("\n[bold cyan]How would you like to pick a destination?[/bold cyan]")
    console.print("  [bold white]1[/bold white] — Pick by flight duration (1–5 hours)")
    console.print("  [bold white]2[/bold white] — Surprise me! (random destination)\n")
    while True:
        choice = console.input("[bold yellow]Select [1/2]: [/bold yellow]").strip()
        if choice == "1":
            return "time"
        elif choice == "2":
            return "random"
        console.print("[red]Please enter 1 or 2.[/red]")


def _prompt_departure(console, db) -> dict | None:
    """Prompt for and validate departure airport ICAO."""
    while True:
        icao = console.input(
            "[bold yellow]Enter departure airport ICAO: [/bold yellow]"
        ).strip().upper()
        ap = db.get_airport(icao)
        if ap:
            console.print(
                f"[green]✓[/green] [cyan]{icao}[/cyan] — {ap['name']} "
                f"({ap['iso_country']}) | {ap['type']} | Elev: {ap.get('elevation_ft','?')}ft\n"
            )
            return ap
        console.print(f"[red]Airport {icao} not found. Try again.[/red]")


def _time_based_picker(console, db, aircraft: dict) -> dict | None:
    from aircraft import nm_range_for_hours, estimate_flight_time

    dep = _prompt_departure(console, db)

    # Hour selection
    console.print("[bold cyan]Select target flight duration:[/bold cyan]")
    for h in range(1, 6):
        min_nm, max_nm = nm_range_for_hours(h, aircraft)
        console.print(
            f"  [bold white]{h}[/bold white] — {h} hour{'s' if h > 1 else ''}  "
            f"([dim]{min_nm:.0f}–{max_nm:.0f} NM[/dim])"
        )
    console.print("  [bold white]6[/bold white] — Custom duration\n")

    while True:
        choice = console.input(
            "[bold yellow]Select duration [1-6]: [/bold yellow]"
        ).strip()
        if choice in [str(i) for i in range(1, 6)]:
            target_hours = int(choice)
            break
        elif choice == "6":
            while True:
                try:
                    target_hours = float(
                        console.input("[bold yellow]Enter hours (e.g. 2.5): [/bold yellow]")
                    )
                    if 0.25 <= target_hours <= 12:
                        break
                    console.print("[red]Please enter a value between 0.25 and 12.[/red]")
                except ValueError:
                    console.print("[red]Invalid number.[/red]")
            break
        console.print("[red]Please enter a number between 1 and 6.[/red]")

    min_nm, max_nm = nm_range_for_hours(target_hours, aircraft)

    console.print(
        f"\n[dim]Searching for airports {min_nm:.0f}–{max_nm:.0f} NM from "
        f"{dep['icao_code']}...[/dim]"
    )

    candidates = db.find_airports_in_range(
        dep["icao_code"],
        min_nm,
        max_nm,
        airport_types=aircraft["type_filter"],
    )

    # Filter by minimum runway length
    candidates = _filter_by_runway(candidates, db, aircraft["min_runway_ft"])

    if candidates.empty:
        console.print(
            "[red]No suitable airports found in this range. "
            "Try a different duration or aircraft.[/red]"
        )
        return None

    # Score and sort: large airports first, then scheduled service, then distance
    candidates = _score_candidates(candidates)

    return _present_candidates(console, candidates, dep, aircraft)


def _random_picker(console, db, aircraft: dict) -> dict | None:
    from aircraft import nm_range_for_hours, estimate_flight_time

    dep = _prompt_departure(console, db)

    console.print("[bold cyan]Random destination options:[/bold cyan]")
    console.print("  [bold white]1[/bold white] — Short hop     (30 min – 1.5 hrs)")
    console.print("  [bold white]2[/bold white] — Medium flight (1.5 – 3 hrs)")
    console.print("  [bold white]3[/bold white] — Long haul     (3 – 6 hrs)")
    console.print("  [bold white]4[/bold white] — Truly random  (any distance)\n")

    while True:
        choice = console.input(
            "[bold yellow]Select range [1-4]: [/bold yellow]"
        ).strip()
        ranges = {
            "1": (0.25, 1.5),
            "2": (1.5, 3.0),
            "3": (3.0, 6.0),
            "4": (0.25, 8.0),
        }
        if choice in ranges:
            min_h, max_h = ranges[choice]
            break
        console.print("[red]Please enter 1, 2, 3, or 4.[/red]")

    min_nm = aircraft["cruise_kts"] * min_h * 0.85
    max_nm = aircraft["cruise_kts"] * max_h * 1.15

    console.print(
        f"\n[dim]Searching {min_nm:.0f}–{max_nm:.0f} NM from "
        f"{dep['icao_code']}...[/dim]"
    )

    candidates = db.find_airports_in_range(
        dep["icao_code"],
        min_nm,
        max_nm,
        airport_types=aircraft["type_filter"],
    )

    candidates = _filter_by_runway(candidates, db, aircraft["min_runway_ft"])

    if candidates.empty:
        console.print("[red]No suitable airports found.[/red]")
        return None

    candidates = _score_candidates(candidates)

    # For random mode — pick one surprise destination from top 30% scored airports
    top_pool = candidates.head(max(10, len(candidates) // 3))
    chosen = top_pool.sample(1).iloc[0].to_dict()

    console.print(
        Panel(
            f"[bold yellow]✈  YOUR SURPRISE DESTINATION[/bold yellow]\n\n"
            f"[bold cyan]{chosen['icao_code']}[/bold cyan] — {chosen['name']}\n"
            f"Country: {chosen['iso_country']} | Type: {chosen['type']} | "
            f"Elev: {chosen.get('elevation_ft', '?')}ft\n"
            f"Distance: {chosen['dist_nm']:.0f} NM | "
            f"Est. time: {estimate_flight_time(chosen['dist_nm'], aircraft)}",
            style="yellow",
        )
    )
    return chosen


# ── Helpers ──────────────────────────────────────────────────

def _filter_by_runway(candidates, db, min_runway_ft: float):
    """Keep only airports with at least one runway meeting minimum length."""
    if candidates.empty:
        return candidates

    valid_icaos = set()
    for icao in candidates["icao_code"].tolist():
        rwys = db.get_runways(icao)
        if rwys.empty:
            # No runway data — include anyway (some airports missing data)
            valid_icaos.add(icao)
            continue
        if rwys["length_ft"].max() >= min_runway_ft:
            valid_icaos.add(icao)

    return candidates[candidates["icao_code"].isin(valid_icaos)].copy()


def _score_candidates(candidates):
    """
    Score airports for quality of destination.
    Higher = better: large airports > scheduled service > medium > small.
    """
    type_score = {
        "large_airport":  300,
        "medium_airport": 200,
        "small_airport":  100,
    }
    candidates = candidates.copy()
    candidates["score"] = candidates["type"].map(type_score).fillna(50)

    # Bonus for scheduled service
    if "scheduled_service" in candidates.columns:
        candidates.loc[candidates["scheduled_service"] == "yes", "score"] += 150

    return candidates.sort_values("score", ascending=False)


def _present_candidates(console, candidates, dep: dict, aircraft: dict) -> dict | None:
    from aircraft import estimate_flight_time

    # Show top 10
    top = candidates.head(10).reset_index(drop=True)

    table = Table(
        title=f"[bold cyan]Destinations from {dep['icao_code']} — "
              f"{aircraft['label']}[/bold cyan]",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#",        style="bold white", width=4)
    table.add_column("ICAO",     style="cyan",       width=6)
    table.add_column("Airport",  style="white",      width=35)
    table.add_column("Country",  style="dim white",  width=8)
    table.add_column("Type",     style="yellow",     width=15)
    table.add_column("Dist NM",  style="green",      width=9)
    table.add_column("Est Time", style="magenta",    width=10)

    type_short = {
        "large_airport":  "Large",
        "medium_airport": "Medium",
        "small_airport":  "Small",
    }

    for i, row in top.iterrows():
        ftime = estimate_flight_time(row["dist_nm"], aircraft)
        table.add_row(
            str(i + 1),
            row["icao_code"],
            row["name"][:34],
            row["iso_country"],
            type_short.get(row["type"], row["type"]),
            f"{row['dist_nm']:.0f}",
            ftime,
        )

    console.print(table)
    console.print("  [bold white]0[/bold white] — Cancel / go back\n")

    while True:
        choice = console.input(
            "[bold yellow]Select destination [1-10] or 0 to cancel: [/bold yellow]"
        ).strip()
        if choice == "0":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(top):
                chosen = top.iloc[idx].to_dict()
                console.print(
                    f"\n[green]✓ Destination selected:[/green] "
                    f"[cyan]{chosen['icao_code']}[/cyan] — {chosen['name']}\n"
                )
                return chosen
        except ValueError:
            pass
        console.print(f"[red]Enter a number between 0 and {min(10, len(top))}.[/red]")