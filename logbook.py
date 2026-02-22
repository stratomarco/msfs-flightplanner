# ============================================================
# Pilot Logbook — Digital flight log with real-world columns
# FAA/ICAO standard format
# Storage: SQLite (logbook.db in project root)
# ============================================================

import os
import sqlite3
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

DB_PATH = "logbook.db"

# Aircraft category codes (maps to our aircraft profile categories)
CATEGORY_MAP = {
    "GA_PISTON": "SEL",   # Single Engine Land (most GA pistons)
    "GA_TWIN":   "MEL",   # Multi Engine Land
    "TURBO":     "TUR",   # Turboprop
    "BIZ_JET":   "JET",   # Jet
    "REGIONAL":  "JET",
    "NARROWBODY":"JET",
    "WIDEBODY":  "JET",
    "MILITARY":  "MIL",
}

# Twin-engine pistons that should be MEL
MEL_AIRCRAFT = {"BE58", "BE60", "AEST", "PA30", "PA44"}


# ── Database setup ────────────────────────────────────────────

def init_db():
    """Create the logbook database and tables if they don't exist."""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS flights (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                date            TEXT NOT NULL,          -- YYYY-MM-DD
                dep_icao        TEXT NOT NULL,
                dep_name        TEXT,
                arr_icao        TEXT NOT NULL,
                arr_name        TEXT,
                alt_icao        TEXT,
                aircraft_type   TEXT NOT NULL,          -- SimBrief code e.g. B738
                aircraft_label  TEXT NOT NULL,          -- Full name
                aircraft_cat    TEXT NOT NULL,          -- SEL/MEL/TUR/JET/MIL
                total_time      REAL NOT NULL,          -- Hours (decimal)
                day_time        REAL NOT NULL DEFAULT 0,
                night_time      REAL NOT NULL DEFAULT 0,
                ifr_time        REAL NOT NULL DEFAULT 0,
                vfr_time        REAL NOT NULL DEFAULT 0,
                xc_time         REAL NOT NULL DEFAULT 0, -- Cross country
                sel_time        REAL NOT NULL DEFAULT 0,
                mel_time        REAL NOT NULL DEFAULT 0,
                tur_time        REAL NOT NULL DEFAULT 0,
                jet_time        REAL NOT NULL DEFAULT 0,
                dist_nm         REAL,
                flight_rules    TEXT,                   -- IFR/VFR
                dep_conditions  TEXT,                   -- VFR/MVFR/IFR/LIFR
                arr_conditions  TEXT,
                remarks         TEXT,
                created_at      TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS totals_cache (
                id              INTEGER PRIMARY KEY CHECK (id = 1),
                total_time      REAL DEFAULT 0,
                day_time        REAL DEFAULT 0,
                night_time      REAL DEFAULT 0,
                ifr_time        REAL DEFAULT 0,
                vfr_time        REAL DEFAULT 0,
                xc_time         REAL DEFAULT 0,
                sel_time        REAL DEFAULT 0,
                mel_time        REAL DEFAULT 0,
                tur_time        REAL DEFAULT 0,
                jet_time        REAL DEFAULT 0,
                flight_count    INTEGER DEFAULT 0,
                last_updated    TEXT
            );

            INSERT OR IGNORE INTO totals_cache (id) VALUES (1);
        """)


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Night time calculation ────────────────────────────────────

def compute_day_night_split(
    dep_lat: float,
    dep_lon: float,
    date_str: str,      # YYYY-MM-DD
    block_time_hrs: float,
    dep_time_utc: datetime | None = None,
) -> tuple[float, float]:
    """
    Compute day and night portions of a flight using
    sunrise/sunset at the departure airport.
    Returns (day_hours, night_hours).
    """
    try:
        from astral import LocationInfo
        from astral.sun import sun

        loc = LocationInfo(
            latitude=dep_lat,
            longitude=dep_lon,
        )
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        s = sun(loc.observer, date=date)

        sunrise = s["sunrise"].replace(tzinfo=timezone.utc)
        sunset  = s["sunset"].replace(tzinfo=timezone.utc)

        # Use provided time or assume current UTC
        if dep_time_utc is None:
            dep_time_utc = datetime.now(timezone.utc)

        arr_time_utc = dep_time_utc + timedelta(hours=block_time_hrs)

        day_minutes   = 0.0
        night_minutes = 0.0
        step = timedelta(minutes=1)
        current = dep_time_utc

        while current < arr_time_utc:
            if sunrise <= current <= sunset:
                day_minutes += 1
            else:
                night_minutes += 1
            current += step

        total_minutes = day_minutes + night_minutes
        if total_minutes == 0:
            return block_time_hrs, 0.0

        day_hrs   = block_time_hrs * (day_minutes   / total_minutes)
        night_hrs = block_time_hrs * (night_minutes / total_minutes)
        return round(day_hrs, 2), round(night_hrs, 2)

    except Exception:
        # astral not available or error — assume all day
        return block_time_hrs, 0.0


# ── Log a flight ─────────────────────────────────────────────

def log_flight(
    dep:           dict,
    arr:           dict,
    aircraft:      dict,
    block_time_hrs: float,
    flight_rules:  str,
    dist_nm:       float,
    alt_airport:   dict | None = None,
    dep_conditions: str = "",
    arr_conditions: str = "",
    remarks:       str = "",
    date_str:      str | None = None,
    dep_time_utc:  datetime | None = None,
) -> int:
    """
    Record a flight in the logbook. Returns the new flight ID.
    """
    init_db()

    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Determine aircraft category
    cat_code = _get_cat_code(aircraft)

    # Cross country — any flight where departure and arrival
    # are more than 50 NM apart (FAA definition)
    xc = block_time_hrs if dist_nm >= 50 else 0.0

    # IFR vs VFR time
    is_ifr = flight_rules.upper() in ("IFR", "MVFR")
    ifr_time = block_time_hrs if is_ifr else 0.0
    vfr_time = block_time_hrs if not is_ifr else 0.0

    # Day / night split
    dep_lat = float(dep.get("latitude_deg", 0))
    dep_lon = float(dep.get("longitude_deg", 0))
    day_time, night_time = compute_day_night_split(
        dep_lat, dep_lon, date_str, block_time_hrs, dep_time_utc
    )

    # Category time columns
    sel_time = block_time_hrs if cat_code == "SEL" else 0.0
    mel_time = block_time_hrs if cat_code == "MEL" else 0.0
    tur_time = block_time_hrs if cat_code == "TUR" else 0.0
    jet_time = block_time_hrs if cat_code == "JET" else 0.0

    with _get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO flights (
                date, dep_icao, dep_name, arr_icao, arr_name,
                alt_icao, aircraft_type, aircraft_label, aircraft_cat,
                total_time, day_time, night_time, ifr_time, vfr_time,
                xc_time, sel_time, mel_time, tur_time, jet_time,
                dist_nm, flight_rules, dep_conditions, arr_conditions, remarks
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
        """, (
            date_str,
            dep["icao_code"], dep.get("name", ""),
            arr["icao_code"], arr.get("name", ""),
            alt_airport["icao_code"] if alt_airport else None,
            aircraft["simbrief_code"], aircraft["label"], cat_code,
            round(block_time_hrs, 2),
            day_time, night_time, ifr_time, vfr_time,
            xc, sel_time, mel_time, tur_time, jet_time,
            round(dist_nm, 0),
            flight_rules.upper(),
            dep_conditions, arr_conditions,
            remarks,
        ))
        flight_id = cur.lastrowid

        # Update totals cache
        conn.execute("""
            UPDATE totals_cache SET
                total_time   = total_time   + ?,
                day_time     = day_time     + ?,
                night_time   = night_time   + ?,
                ifr_time     = ifr_time     + ?,
                vfr_time     = vfr_time     + ?,
                xc_time      = xc_time      + ?,
                sel_time     = sel_time     + ?,
                mel_time     = mel_time     + ?,
                tur_time     = tur_time     + ?,
                jet_time     = jet_time     + ?,
                flight_count = flight_count + 1,
                last_updated = datetime('now')
            WHERE id = 1
        """, (
            round(block_time_hrs, 2),
            day_time, night_time, ifr_time, vfr_time,
            xc, sel_time, mel_time, tur_time, jet_time,
        ))

    return flight_id


# ── Display logbook ───────────────────────────────────────────

def display_recent(console: Console, n: int = 20):
    """Show the last N flights in logbook format."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM flights
            ORDER BY date DESC, id DESC
            LIMIT ?
        """, (n,)).fetchall()

    if not rows:
        console.print("[yellow]Logbook is empty — no flights recorded yet.[/yellow]")
        return

    table = Table(
        title=f"[bold white]✈  Pilot Logbook — Last {min(n, len(rows))} Flights[/bold white]",
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
    )

    table.add_column("Date",       style="white",       width=12)
    table.add_column("From",       style="cyan",        width=6)
    table.add_column("To",         style="cyan",        width=6)
    table.add_column("Aircraft",   style="white",       width=22)
    table.add_column("Cat",        style="yellow",      width=5)
    table.add_column("Total",      style="green",       width=6)
    table.add_column("Day",        style="yellow",      width=6)
    table.add_column("Night",      style="blue",        width=6)
    table.add_column("IFR",        style="red",         width=6)
    table.add_column("VFR",        style="green",       width=6)
    table.add_column("XC",         style="magenta",     width=6)
    table.add_column("NM",         style="dim",         width=6)
    table.add_column("Rules",      style="dim",         width=5)

    for row in rows:
        table.add_row(
            row["date"],
            row["dep_icao"],
            row["arr_icao"],
            row["aircraft_label"][:21],
            row["aircraft_cat"],
            _fmt_time(row["total_time"]),
            _fmt_time(row["day_time"]),
            _fmt_time(row["night_time"]),
            _fmt_time(row["ifr_time"]),
            _fmt_time(row["vfr_time"]),
            _fmt_time(row["xc_time"]),
            str(int(row["dist_nm"] or 0)),
            row["flight_rules"] or "",
        )

    console.print(table)
    display_totals(console)


def display_totals(console: Console):
    """Show running totals in logbook footer format."""
    init_db()
    with _get_conn() as conn:
        t = conn.execute("SELECT * FROM totals_cache WHERE id = 1").fetchone()

    if not t or t["flight_count"] == 0:
        return

    console.print(Panel(
        f"  Flights    : [bold white]{t['flight_count']}[/bold white]\n"
        f"  Total Time : [bold green]{_fmt_time(t['total_time'])}[/bold green]   "
        f"XC: [magenta]{_fmt_time(t['xc_time'])}[/magenta]\n"
        f"  Day        : [yellow]{_fmt_time(t['day_time'])}[/yellow]   "
        f"Night: [blue]{_fmt_time(t['night_time'])}[/blue]\n"
        f"  IFR        : [red]{_fmt_time(t['ifr_time'])}[/red]     "
        f"VFR: [green]{_fmt_time(t['vfr_time'])}[/green]\n"
        f"  SEL        : [dim]{_fmt_time(t['sel_time'])}[/dim]   "
        f"MEL: [dim]{_fmt_time(t['mel_time'])}[/dim]   "
        f"Turboprop: [dim]{_fmt_time(t['tur_time'])}[/dim]   "
        f"Jet: [dim]{_fmt_time(t['jet_time'])}[/dim]",
        title="[bold white]Logbook Totals[/bold white]",
        style="blue",
    ))


def display_airport_stats(console: Console, top_n: int = 10):
    """Show most visited airports."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT icao, name, visits FROM (
                SELECT dep_icao AS icao, dep_name AS name, COUNT(*) AS visits
                FROM flights GROUP BY dep_icao
                UNION ALL
                SELECT arr_icao, arr_name, COUNT(*) FROM flights GROUP BY arr_icao
            )
            GROUP BY icao
            ORDER BY SUM(visits) DESC
            LIMIT ?
        """, (top_n,)).fetchall()

    if not rows:
        return

    table = Table(
        title=f"[bold white]Top {top_n} Airports[/bold white]",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("ICAO",   style="cyan",  width=7)
    table.add_column("Name",   style="white", width=35)
    table.add_column("Visits", style="green", width=8)

    for row in rows:
        table.add_row(row["icao"], row["name"] or "", str(row["visits"]))

    console.print(table)


def prompt_log_flight(console: Console, dep, arr, aircraft,
                       block_time_hrs, flight_rules, dist_nm,
                       alt_airport, dep_metar, arr_metar) -> bool:
    """
    Ask user if they want to log this flight, collect remarks,
    then save to logbook. Returns True if logged.
    """
    console.print("\n[bold underline]LOGBOOK[/bold underline]")

    log = console.input(
        "[bold yellow]Log this flight in your logbook? [Y/n]: [/bold yellow]"
    ).strip().lower()

    if log not in ("", "y", "yes"):
        console.print("  [dim]Flight not logged.[/dim]")
        return False

    remarks = console.input(
        "[bold yellow]Remarks (optional, press Enter to skip): [/bold yellow]"
    ).strip()

    from metar import parse_flight_category
    dep_cat = parse_flight_category(dep_metar) if dep_metar else ""
    arr_cat = parse_flight_category(arr_metar) if arr_metar else ""

    flight_id = log_flight(
        dep            = dep,
        arr            = arr,
        aircraft       = aircraft,
        block_time_hrs = block_time_hrs,
        flight_rules   = flight_rules,
        dist_nm        = dist_nm,
        alt_airport    = alt_airport,
        dep_conditions = dep_cat,
        arr_conditions = arr_cat,
        remarks        = remarks,
    )

    console.print(
        f"  [green]✓ Flight #{flight_id} logged —[/green] "
        f"[cyan]{dep['icao_code']}[/cyan] → [cyan]{arr['icao_code']}[/cyan]  "
        f"[magenta]{_fmt_time(block_time_hrs)}[/magenta]"
    )

    display_totals(console)
    return True


# ── Helpers ───────────────────────────────────────────────────

def _fmt_time(hours: float) -> str:
    """Format decimal hours as H:MM logbook style."""
    if not hours:
        return "0:00"
    h = int(hours)
    m = int(round((hours - h) * 60))
    return f"{h}:{m:02d}"


def _get_cat_code(aircraft: dict) -> str:
    """Determine SEL/MEL/TUR/JET/MIL from aircraft profile."""
    # Explicit MEL by SimBrief code
    if aircraft.get("simbrief_code", "") in MEL_AIRCRAFT:
        return "MEL"
    cat = aircraft.get("category", "GA_PISTON")
    return CATEGORY_MAP.get(cat, "SEL")