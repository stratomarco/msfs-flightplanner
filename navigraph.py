# ============================================================
# Navigraph Charts Integration
# Deeplink-based — requires active Navigraph subscription
# No API key needed
# ============================================================

from rich.table import Table
from rich.panel import Panel

# Base URLs
CHARTS_BASE   = "https://charts.navigraph.com/charts"
CHARTS_APP    = "navigraph-charts://charts"   # Desktop app deeplink

# Chart type codes
CHART_TYPES = {
    "APT": "Airport Diagram",
    "DEP": "SID / Departure",
    "ARR": "STAR / Arrival",
    "APR": "Approach",
    "AOI": "Area / Overview",
}


def build_chart_links(icao: str) -> dict:
    """
    Build all chart deeplinks for a given airport ICAO.
    Returns dict of {chart_type_label: (web_url, app_url)}
    """
    links = {}
    for code, label in CHART_TYPES.items():
        web_url = f"{CHARTS_BASE}?icao={icao}&type={code}"
        app_url = f"{CHARTS_APP}?icao={icao}&type={code}"
        links[label] = {"web": web_url, "app": app_url, "code": code}
    return links


def build_airport_chart_url(icao: str, chart_type: str = "APT") -> str:
    """Single chart URL for a specific type."""
    return f"{CHARTS_BASE}?icao={icao}&type={chart_type}"


def display_chart_links(console, dep_icao: str, arr_icao: str, alt_icao: str | None):
    """
    Display a clean table of Navigraph chart links for the route.
    Grouped by airport role: departure, arrival, alternate.
    """
    airports = [
        (dep_icao, "Departure", "cyan"),
        (arr_icao, "Arrival",   "green"),
    ]
    if alt_icao:
        airports.append((alt_icao, "Alternate", "yellow"))

    table = Table(
        title="[bold white]Navigraph Charts[/bold white]",
        show_header=True,
        header_style="bold white",
        show_lines=True,
    )
    table.add_column("Role",       style="bold",       width=12)
    table.add_column("ICAO",       style="cyan",       width=7)
    table.add_column("Chart Type", style="white",      width=20)
    table.add_column("Open in Browser",                width=55)

    for icao, role, color in airports:
        links = build_chart_links(icao)
        first = True
        for label, urls in links.items():
            role_cell = f"[{color}]{role}[/{color}]" if first else ""
            icao_cell = f"[{color}]{icao}[/{color}]"  if first else ""
            table.add_row(
                role_cell,
                icao_cell,
                label,
                f"[link={urls['web']}]{urls['web']}[/link]",
            )
            first = False

    console.print(table)
    console.print(
        "[dim]Tip: These links open directly in Navigraph Charts web. "
        "Make sure you're signed in at navigraph.com first.[/dim]\n"
    )


def display_key_charts(console, dep_icao: str, arr_icao: str, alt_icao: str | None):
    """
    Display a focused, minimal set of the most useful charts only:
    DEP → SID, ARR → STAR + Approach, ALT → Approach + Airport
    This is the quick-reference version shown in the briefing.
    """
    lines = []

    # Departure — SID + Airport diagram
    lines.append(
        f"  [cyan][DEP] {dep_icao}[/cyan]  "
        f"Airport:  [link={build_airport_chart_url(dep_icao, 'APT')}]"
        f"{build_airport_chart_url(dep_icao, 'APT')}[/link]"
    )
    lines.append(
        f"  [cyan][DEP] {dep_icao}[/cyan]  "
        f"SID:      [link={build_airport_chart_url(dep_icao, 'DEP')}]"
        f"{build_airport_chart_url(dep_icao, 'DEP')}[/link]"
    )

    # Arrival — STAR + Approach
    lines.append(
        f"  [green][ARR] {arr_icao}[/green]  "
        f"STAR:     [link={build_airport_chart_url(arr_icao, 'ARR')}]"
        f"{build_airport_chart_url(arr_icao, 'ARR')}[/link]"
    )
    lines.append(
        f"  [green][ARR] {arr_icao}[/green]  "
        f"Approach: [link={build_airport_chart_url(arr_icao, 'APR')}]"
        f"{build_airport_chart_url(arr_icao, 'APR')}[/link]"
    )

    # Alternate — Approach + Airport
    if alt_icao:
        lines.append(
            f"  [yellow][ALT] {alt_icao}[/yellow]  "
            f"Airport:  [link={build_airport_chart_url(alt_icao, 'APT')}]"
            f"{build_airport_chart_url(alt_icao, 'APT')}[/link]"
        )
        lines.append(
            f"  [yellow][ALT] {alt_icao}[/yellow]  "
            f"Approach: [link={build_airport_chart_url(alt_icao, 'APR')}]"
            f"{build_airport_chart_url(alt_icao, 'APR')}[/link]"
        )

    console.print(Panel(
        "\n".join(lines),
        title="[bold white]📋  Navigraph Charts — Quick Reference[/bold white]",
        style="white",
    ))