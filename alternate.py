# ============================================================
# Alternate Airport Selection — IFR Real-World Logic
# FAR 91.167 / ICAO Annex 2 alternate minima
# ============================================================

from geopy.distance import geodesic
from metar import get_metar, parse_flight_category, get_metar_batch
from rich.panel import Panel
from rich.table import Table


# ── Alternate requirement thresholds ────────────────────────
# FAR 91.167: alternate required if destination wx forecast
# within 1hr of ETA is below 2000ft ceiling OR 3SM visibility.
# We evaluate using current METAR as proxy.
ALT_REQUIRED_CEILING_FT  = 2000
ALT_REQUIRED_VIS_SM      = 3.0

# Alternate airport minima (what the alternate must be forecast to have)
ALT_MINIMA_PRECISION     = {"ceiling_ft": 600,  "vis_sm": 2.0}   # ILS/LPV
ALT_MINIMA_NONPRECISION  = {"ceiling_ft": 800,  "vis_sm": 2.0}   # RNAV/VOR
ALT_MINIMA_VISUAL        = {"ceiling_ft": 1000, "vis_sm": 3.0}   # No IAP

# Search range for alternate (NM from destination)
ALT_MIN_NM = 30
ALT_MAX_NM = 200


def alternate_required(arr_metar: dict | None) -> bool:
    """
    Determine if an alternate is required based on arrival METAR.
    Returns True if conditions are at or below alternate-required thresholds.
    """
    if arr_metar is None:
        return True  # No wx data — file alternate to be safe

    cat = parse_flight_category(arr_metar)

    # IFR or LIFR always requires alternate
    if cat in ("IFR", "LIFR"):
        return True

    # Check ceiling
    ceiling = _extract_ceiling(arr_metar)
    if ceiling is not None and ceiling < ALT_REQUIRED_CEILING_FT:
        return True

    # Check visibility
    vis = _extract_visibility(arr_metar)
    if vis is not None and vis < ALT_REQUIRED_VIS_SM:
        return True

    return False


def find_alternate(
    console,
    db,
    arr_icao: str,
    arr_metar: dict | None,
    aircraft: dict,
) -> dict | None:
    """
    Find the best alternate airport for the given arrival airport.
    Returns selected alternate airport dict or None.
    """
    console.print(
        "\n[bold yellow]⚠  ALTERNATE REQUIRED[/bold yellow] — "
        "Destination weather is at or below alternate-required minima.\n"
    )
    _explain_requirement(console, arr_metar)

    # Search for candidates around the destination
    console.print(
        f"\n[dim]Searching for alternates {ALT_MIN_NM}–{ALT_MAX_NM} NM "
        f"from {arr_icao}...[/dim]"
    )

    candidates = db.find_airports_in_range(
        arr_icao,
        ALT_MIN_NM,
        ALT_MAX_NM,
        airport_types=["large_airport", "medium_airport"],
    )

    # Filter by runway length
    candidates = _filter_by_runway(candidates, db, aircraft["min_runway_ft"])

    if candidates.empty:
        # Widen search if nothing found
        console.print("[dim]Widening search to small airports...[/dim]")
        candidates = db.find_airports_in_range(
            arr_icao, ALT_MIN_NM, ALT_MAX_NM,
            airport_types=aircraft["type_filter"],
        )
        candidates = _filter_by_runway(candidates, db, aircraft["min_runway_ft"])

    if candidates.empty:
        console.print("[red]No suitable alternate airports found in range.[/red]")
        return None

    # Fetch METARs for top 15 candidates (batch where possible)
    top_candidates = candidates.head(15)
    icao_list = top_candidates["icao_code"].tolist()

    console.print(f"[dim]Fetching weather for {len(icao_list)} candidate alternates...[/dim]")
    metars = _fetch_metars_safe(icao_list)

    # Score each candidate
    scored = _score_alternates(top_candidates, metars, arr_metar)

    if scored.empty:
        console.print("[red]No alternates met weather criteria.[/red]")
        return None

    # Present top 6 with weather
    return _present_alternates(console, scored, arr_icao, metars, aircraft)


def describe_alternate_requirement(console, arr_metar: dict | None):
    """
    Print a one-line summary of whether an alternate is required.
    Call this regardless of outcome to inform the pilot.
    """
    if alternate_required(arr_metar):
        console.print(
            "  [bold yellow]Alternate:[/bold yellow] [yellow]REQUIRED[/yellow] "
            "(destination wx below 2000ft / 3SM threshold)"
        )
    else:
        console.print(
            "  [bold green]Alternate:[/bold green] [green]NOT REQUIRED[/green] "
            "(destination wx above alternate-required minima)"
        )
        console.print(
            "  [dim]Note: Filing one is always good practice.[/dim]"
        )


# ── Internal helpers ─────────────────────────────────────────

def _explain_requirement(console, arr_metar: dict | None):
    """Print the specific reason alternate is required."""
    if arr_metar is None:
        console.print("  [dim]Reason: No METAR available for destination.[/dim]")
        return

    cat = parse_flight_category(arr_metar)
    ceiling = _extract_ceiling(arr_metar)
    vis = _extract_visibility(arr_metar)

    parts = []
    if cat in ("IFR", "LIFR"):
        parts.append(f"flight category is [bold red]{cat}[/bold red]")
    if ceiling is not None and ceiling < ALT_REQUIRED_CEILING_FT:
        parts.append(f"ceiling {ceiling}ft < 2000ft")
    if vis is not None and vis < ALT_REQUIRED_VIS_SM:
        parts.append(f"visibility {vis}SM < 3SM")

    if parts:
        console.print(f"  [dim]Reason: {' | '.join(parts)}[/dim]")


def _extract_ceiling(metar: dict) -> int | None:
    """
    Extract ceiling in feet from METAR.
    Ceiling = lowest BKN or OVC layer.
    """
    try:
        raw = metar.get("rawOb", "")
        import re
        layers = re.findall(r'(BKN|OVC)(\d{3})', raw)
        if layers:
            return int(layers[0][1]) * 100  # convert hundreds to feet
    except Exception:
        pass
    return None


def _extract_visibility(metar: dict) -> float | None:
    """Extract visibility in statute miles from METAR dict."""
    try:
        vis = metar.get("visib")
        if vis is not None:
            return float(vis)
    except (TypeError, ValueError):
        pass
    return None


def _filter_by_runway(candidates, db, min_runway_ft: float):
    """Keep only airports with a runway meeting minimum length."""
    if candidates.empty:
        return candidates
    valid = set()
    for icao in candidates["icao_code"].tolist():
        rwys = db.get_runways(icao)
        if rwys.empty or rwys["length_ft"].max() >= min_runway_ft:
            valid.add(icao)
    return candidates[candidates["icao_code"].isin(valid)].copy()


def _fetch_metars_safe(icao_list: list) -> dict:
    """Fetch METARs for a list of ICAOs, return {icao: metar_dict}."""
    result = {}
    try:
        from metar import get_metar_batch
        batch = get_metar_batch(icao_list)
        if batch:
            for m in batch:
                icao = m.get("icaoId") or m.get("station")
                if icao:
                    result[icao] = m
    except Exception:
        pass

    # Fallback: fetch individually for any missing
    for icao in icao_list:
        if icao not in result:
            try:
                m = get_metar(icao)
                if m:
                    result[icao] = m
            except Exception:
                pass
    return result


def _score_alternates(candidates, metars: dict, arr_metar: dict | None):
    """
    Score and sort candidate alternates.
    Factors: airport type, wx better than destination, wx above alternate minima.
    """
    import pandas as pd

    type_score = {"large_airport": 300, "medium_airport": 200, "small_airport": 100}
    arr_cat_order = {"VFR": 0, "MVFR": 1, "IFR": 2, "LIFR": 3, "UNKN": 1}
    arr_cat = parse_flight_category(arr_metar) if arr_metar else "UNKN"

    rows = []
    for _, row in candidates.iterrows():
        icao = row["icao_code"]
        score = type_score.get(row["type"], 50)

        metar = metars.get(icao)
        if metar:
            cat = parse_flight_category(metar)
            cat_idx = arr_cat_order.get(cat, 1)
            arr_idx = arr_cat_order.get(arr_cat, 1)

            # Bonus if weather is better than destination
            if cat_idx < arr_idx:
                score += 200
            elif cat_idx == arr_idx:
                score += 50

            # Verify meets alternate minima (assume non-precision approach)
            ceiling = _extract_ceiling(metar)
            vis = _extract_visibility(metar)
            minima = ALT_MINIMA_NONPRECISION
            if ceiling is not None and ceiling < minima["ceiling_ft"]:
                score -= 500  # Penalize — doesn't meet minima
            if vis is not None and vis < minima["vis_sm"]:
                score -= 500
        else:
            # No METAR — neutral, slight penalty
            score -= 25

        if "scheduled_service" in row and row["scheduled_service"] == "yes":
            score += 100

        rows.append({**row.to_dict(), "alt_score": score, "alt_metar": metar})

    df = pd.DataFrame(rows)
    return df[df["alt_score"] > 0].sort_values("alt_score", ascending=False)


def _present_alternates(console, scored, arr_icao: str, metars: dict, aircraft: dict) -> dict | None:
    from aircraft import estimate_flight_time

    top = scored.head(6).reset_index(drop=True)

    CATEGORY_COLORS = {
        "VFR": "bold green", "MVFR": "bold yellow",
        "IFR": "bold red",   "LIFR": "bold magenta", "UNKN": "white"
    }

    table = Table(
        title=f"[bold yellow]Alternate Airports — from {arr_icao}[/bold yellow]",
        show_header=True,
        header_style="bold yellow",
    )
    table.add_column("#",         style="bold white", width=4)
    table.add_column("ICAO",      style="cyan",       width=7)
    table.add_column("Airport",   style="white",      width=32)
    table.add_column("Country",   style="dim white",  width=8)
    table.add_column("Dist NM",   style="green",      width=9)
    table.add_column("Wx",        style="white",      width=8)
    table.add_column("Raw METAR", style="dim",        width=35)

    for i, row in top.iterrows():
        metar = row.get("alt_metar")
        if metar:
            cat = parse_flight_category(metar)
            color = CATEGORY_COLORS.get(cat, "white")
            cat_str = f"[{color}]{cat}[/{color}]"
            raw = (metar.get("rawOb") or "")[:34]
        else:
            cat_str = "[dim]N/A[/dim]"
            raw = "[dim]No METAR[/dim]"

        table.add_row(
            str(i + 1),
            row["icao_code"],
            row["name"][:31],
            row["iso_country"],
            f"{row['dist_nm']:.0f}",
            cat_str,
            raw,
        )

    console.print(table)
    console.print(
        "\n[dim]Alternates are scored by: weather improvement over destination, "
        "airport type, and non-precision approach minima (800ft / 2SM).[/dim]"
    )
    console.print("  [bold white]0[/bold white] — Skip alternate selection\n")

    while True:
        choice = console.input(
            "[bold yellow]Select alternate [1-6] or 0 to skip: [/bold yellow]"
        ).strip()
        if choice == "0":
            console.print(
                "[yellow]No alternate selected. Proceed with caution.[/yellow]"
            )
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(top):
                chosen = top.iloc[idx].to_dict()
                console.print(
                    f"\n[green]✓ Alternate selected:[/green] "
                    f"[cyan]{chosen['icao_code']}[/cyan] — {chosen['name']}\n"
                )
                return chosen
        except ValueError:
            pass
        console.print(f"[red]Enter a number between 0 and {min(6, len(top))}.[/red]")