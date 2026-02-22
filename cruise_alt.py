# ============================================================
# Cruise altitude selector
# Hemispherical rules: FAA FAR 91.159 (VFR) / 91.179 (IFR)
# ============================================================

import math


def magnetic_course(dep: dict, arr: dict) -> float:
    """
    Compute true course between two airports (degrees 0-359).
    We use true course as a proxy for magnetic — close enough
    for hemispherical rule purposes without a magnetic variation DB.
    """
    lat1 = math.radians(float(dep["latitude_deg"]))
    lat2 = math.radians(float(arr["latitude_deg"]))
    dlon = math.radians(
        float(arr["longitude_deg"]) - float(dep["longitude_deg"])
    )

    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def hemispherical_direction(course_deg: float) -> str:
    """Returns 'EAST' (0-179°) or 'WEST' (180-359°)."""
    return "EAST" if course_deg < 180 else "WEST"


def vfr_altitudes(course_deg: float, min_alt_ft: int = 3500,
                  max_alt_ft: int = 17500) -> list[dict]:
    """
    Return valid VFR hemispherical altitudes for the given course.
    EAST (0-179°): Odd thousands + 500  →  3500, 5500, 7500 ...
    WEST (180-359°): Even thousands + 500 →  4500, 6500, 8500 ...
    """
    direction = hemispherical_direction(course_deg)
    altitudes = []

    if direction == "EAST":
        # Odd thousands + 500: 3500, 5500, 7500, 9500 ...
        start = 3500
        step  = 2000
    else:
        # Even thousands + 500: 4500, 6500, 8500, 10500 ...
        start = 4500
        step  = 2000

    alt = start
    while alt <= max_alt_ft:
        if alt >= min_alt_ft:
            altitudes.append({
                "ft":    alt,
                "label": f"{alt:,} ft  (FL{alt // 100:03d})",
                "fl":    alt // 100,
            })
        alt += step

    return altitudes


def ifr_altitudes(course_deg: float, min_alt_ft: int = 2000,
                  max_alt_ft: int = 45000) -> list[dict]:
    """
    Return valid IFR hemispherical flight levels for the given course.
    EAST (0-179°): Odd thousands  →  FL030, FL050, FL070 ...
    WEST (180-359°): Even thousands → FL040, FL060, FL080 ...

    Below FL290: 1000ft separation.
    FL290+: RVSM 1000ft separation maintained but alternates odd/even.
    """
    direction = hemispherical_direction(course_deg)
    altitudes = []

    if direction == "EAST":
        start = 3000    # FL030
        step  = 2000
    else:
        start = 4000    # FL040
        step  = 2000

    alt = start
    while alt <= max_alt_ft:
        if alt >= min_alt_ft:
            fl = alt // 100
            altitudes.append({
                "ft":    alt,
                "label": f"FL{fl:03d}  ({alt:,} ft)",
                "fl":    fl,
            })
        alt += step

    return altitudes


def suggest_cruise_alt(dep: dict, arr: dict, aircraft: dict,
                       flight_rules: str) -> dict:
    """
    Given dep, arr, aircraft and flight rules, return:
      - course_deg: magnetic course
      - direction: EAST or WEST
      - options: list of altitude dicts
      - default: the best default altitude for this aircraft
    """
    course  = magnetic_course(dep, arr)
    direct  = hemispherical_direction(course)

    # Terrain / minimum safe altitude — use elevation of higher airport + 1000ft
    dep_elev = float(dep.get("elevation_ft") or dep.get("elev_ft") or 0)
    arr_elev = float(arr.get("elevation_ft") or arr.get("elev_ft") or 0)
    min_safe = max(dep_elev, arr_elev) + 1000

    # For VFR, round up to nearest valid hemispherical altitude above min_safe
    # For IFR, allow a wider range
    ac_cruise = aircraft.get("cruise_alt", 8000)

    if flight_rules == "VFR":
        options = vfr_altitudes(course, min_alt_ft=max(3500, int(min_safe)))
        # Default: first option at or above aircraft's preferred cruise
        default = next(
            (o for o in options if o["ft"] >= min(ac_cruise, 9500)),
            options[0] if options else {"ft": 3500, "label": "3,500 ft", "fl": 35}
        )
    else:
        options = ifr_altitudes(course, min_alt_ft=max(2000, int(min_safe)))
        # Default: closest IFR altitude to aircraft's preferred cruise
        default = min(options, key=lambda o: abs(o["ft"] - ac_cruise)) if options else \
                  {"ft": ac_cruise, "label": f"FL{ac_cruise//100:03d}", "fl": ac_cruise//100}

    return {
        "course_deg": round(course, 1),
        "direction":  direct,
        "options":    options,
        "default":    default,
    }