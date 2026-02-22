# ============================================================
# Fuel Planning Engine
# Computes trip fuel using POH performance tables
# Phases: Taxi → Climb → Cruise → Descent → Reserve
# ============================================================

from poh_data import get_poh, get_cruise_row, fuel_unit_label


def compute_fuel_plan(dep, arr, aircraft, dist_nm, cruise_fl, flight_rules="IFR"):
    """
    Compute a full fuel plan.
    Returns dict with phase breakdown and totals, or None if no POH data.
    """
    poh = get_poh(aircraft.get("simbrief_code", ""))
    if not poh:
        return None

    # Determine which fuel key this aircraft uses
    fuel_key = "fuel_pph" if poh["fuel_unit"] == "lbs" else "fuel_gph"
    unit      = poh["fuel_unit"]   # "lbs" or "gal"
    unit_hr   = fuel_unit_label(poh)

    # ── Taxi ──────────────────────────────────────────────
    taxi = poh["taxi_fuel"]

    # ── Climb ─────────────────────────────────────────────
    dep_elev   = float(dep.get("elevation_ft") or dep.get("elev_ft") or 0)
    climb_to   = cruise_fl * 100
    climb_delta = max(0, climb_to - dep_elev)

    climb_fpm   = poh["climb"]["fpm"]
    climb_ktas  = poh["climb"]["ktas"]
    climb_burn  = poh["climb"].get(fuel_key, 0)

    climb_time_hr  = climb_delta / climb_fpm / 60
    climb_dist_nm  = climb_ktas  * climb_time_hr
    climb_fuel     = climb_burn  * climb_time_hr

    # ── Cruise row at target FL ────────────────────────────
    cruise_row   = get_cruise_row(poh, cruise_fl)
    cruise_ktas  = cruise_row.get("ktas",      aircraft.get("cruise_kts", 250))
    cruise_burn  = cruise_row.get(fuel_key,    0)
    power_pct    = cruise_row.get("power_pct", 75)
    cruise_notes = cruise_row.get("notes",     "")

    # ── Descent ───────────────────────────────────────────
    arr_elev       = float(arr.get("elevation_ft") or arr.get("elev_ft") or 0)
    descent_delta  = max(0, climb_to - arr_elev)
    desc_fpm       = poh["descent"]["fpm"]
    desc_ktas      = poh["descent"]["ktas"]
    desc_burn      = poh["descent"].get(fuel_key, 0)

    descent_time_hr  = descent_delta / desc_fpm / 60
    descent_dist_nm  = desc_ktas * descent_time_hr
    descent_fuel     = desc_burn * descent_time_hr

    # ── Cruise leg ────────────────────────────────────────
    cruise_dist_nm = max(0, dist_nm - climb_dist_nm - descent_dist_nm)
    cruise_time_hr = cruise_dist_nm / cruise_ktas if cruise_ktas > 0 else 0
    cruise_fuel    = cruise_burn * cruise_time_hr

    # ── Totals ────────────────────────────────────────────
    total_time_hr  = climb_time_hr + cruise_time_hr + descent_time_hr
    trip_fuel      = climb_fuel + cruise_fuel + descent_fuel
    contingency    = trip_fuel * (poh["contingency_pct"] / 100)
    reserve        = poh["reserve_fuel"]
    block_fuel     = taxi + trip_fuel + contingency + reserve

    usable         = poh["fuel_capacity"]
    fuel_ok        = block_fuel <= usable
    endurance_hr   = (usable - taxi - reserve) / cruise_burn if cruise_burn > 0 else 0
    max_range_nm   = endurance_hr * cruise_ktas

    return {
        "poh":              poh,
        "fuel_key":         fuel_key,
        "unit":             unit,
        "unit_hr":          unit_hr,
        "cruise_fl":        cruise_fl,
        "cruise_ktas":      cruise_ktas,
        "cruise_notes":     cruise_notes,
        "power_pct":        power_pct,
        "taxi_fuel":        taxi,
        "climb_fuel":       climb_fuel,
        "climb_time_hr":    climb_time_hr,
        "climb_dist_nm":    climb_dist_nm,
        "climb_burn_rate":  climb_burn,
        "cruise_fuel":      cruise_fuel,
        "cruise_time_hr":   cruise_time_hr,
        "cruise_dist_nm":   cruise_dist_nm,
        "cruise_burn_rate": cruise_burn,
        "descent_fuel":     descent_fuel,
        "descent_time_hr":  descent_time_hr,
        "descent_dist_nm":  descent_dist_nm,
        "descent_burn_rate":desc_burn,
        "trip_fuel":        trip_fuel,
        "contingency":      contingency,
        "reserve":          reserve,
        "block_fuel":       block_fuel,
        "total_time_hr":    total_time_hr,
        "usable_capacity":  usable,
        "fuel_ok":          fuel_ok,
        "max_range_nm":     max_range_nm,
        "endurance_hr":     endurance_hr,
    }


def format_fuel_plan(fp: dict) -> str:
    """Full phase-by-phase breakdown for the popup window."""
    if not fp:
        return "No POH data available for this aircraft."

    poh  = fp["poh"]
    unit = fp["unit"]   # "gal" or "lbs"
    uhr  = fp["unit_hr"]

    def _t(hrs):
        h = int(hrs)
        m = int(round((hrs - h) * 60))
        return f"{h}:{m:02d}"

    def _f(v):
        return f"{v:,.0f}"

    # Convert to gal for lbs aircraft for pilot reference
    def _gal(v):
        if unit == "lbs":
            return f"  ({v/6.7:.0f} gal)"
        return ""

    lines = [
        f"{'─'*58}",
        f"  {poh['label']}",
        f"  Tier {poh['tier']} data  |  {poh['source'][:52]}",
        f"{'─'*58}",
        f"",
        f"  CRUISE  FL{fp['cruise_fl']:03d}  ·  {fp['cruise_ktas']} KTAS  ·  {fp['power_pct']}% power",
        f"  {fp['cruise_notes']}",
        f"",
        f"  {'PHASE':<12} {'TIME':>6}  {'DIST':>7}  {'FUEL':>12}  {'BURN RATE':>12}",
        f"  {'─'*56}",
        f"  {'Taxi':<12} {'—':>6}  {'—':>7}  {_f(fp['taxi_fuel']):>9} {unit}",
        f"  {'Climb':<12} {_t(fp['climb_time_hr']):>6}  {fp['climb_dist_nm']:>5.0f} NM"
        f"  {_f(fp['climb_fuel']):>9} {unit}  {_f(fp['climb_burn_rate']):>9} {uhr}",
        f"  {'Cruise':<12} {_t(fp['cruise_time_hr']):>6}  {fp['cruise_dist_nm']:>5.0f} NM"
        f"  {_f(fp['cruise_fuel']):>9} {unit}  {_f(fp['cruise_burn_rate']):>9} {uhr}",
        f"  {'Descent':<12} {_t(fp['descent_time_hr']):>6}  {fp['descent_dist_nm']:>5.0f} NM"
        f"  {_f(fp['descent_fuel']):>9} {unit}  {_f(fp['descent_burn_rate']):>9} {uhr}",
        f"  {'─'*56}",
        f"  {'Trip Fuel':<12} {_t(fp['total_time_hr']):>6}  {fp['cruise_dist_nm']+fp['climb_dist_nm']+fp['descent_dist_nm']:>5.0f} NM"
        f"  {_f(fp['trip_fuel']):>9} {unit}{_gal(fp['trip_fuel'])}",
        f"  {'Contingency':<12} ({poh['contingency_pct']}%)        "
        f"  {_f(fp['contingency']):>9} {unit}",
        f"  {'Reserve':<12}                "
        f"  {_f(fp['reserve']):>9} {unit}",
        f"  {'─'*56}",
        f"  {'BLOCK FUEL':<12}             "
        f"  {_f(fp['block_fuel']):>9} {unit}{_gal(fp['block_fuel'])}",
        f"  {'Capacity':<12}             "
        f"  {_f(fp['usable_capacity']):>9} {unit}",
        f"",
    ]

    if not fp["fuel_ok"]:
        shortage = fp["block_fuel"] - fp["usable_capacity"]
        lines.append(f"  ⚠  EXCEEDS CAPACITY by {_f(shortage)} {unit} — reduce payload or add stop")
    else:
        margin = fp["usable_capacity"] - fp["block_fuel"]
        lines.append(f"  ✓  Margin: {_f(margin)} {unit} above block fuel")

    lines += [
        f"",
        f"  Max range at this power: {fp['max_range_nm']:.0f} NM"
        f"  ({_t(fp['endurance_hr'])} endurance)",
    ]

    return "\n".join(lines)


def summary_line(fp: dict) -> str:
    """Compact one-liner for the Route card."""
    if not fp:
        return "⛽  Fuel: No POH data"

    unit = fp["unit"]
    ok   = "✓" if fp["fuel_ok"] else "⚠"
    tier = fp["poh"]["tier"]

    # Show gallons in parentheses for lbs aircraft
    if unit == "lbs":
        blk = f"{fp['block_fuel']:.0f} lbs ({fp['block_fuel']/6.7:.0f} gal)"
        trp = f"{fp['trip_fuel']:.0f}"
        rsv = f"{fp['reserve']:.0f}"
    else:
        blk = f"{fp['block_fuel']:.1f} gal"
        trp = f"{fp['trip_fuel']:.1f}"
        rsv = f"{fp['reserve']:.1f}"

    return (
        f"{ok}  Block: {blk}  "
        f"(Trip {trp} + Rsv {rsv} {unit})  "
        f"Burn: {fp['cruise_burn_rate']:.0f} {fp['unit_hr']}  "
        f"[T{tier}]"
    )