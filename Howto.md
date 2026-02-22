# MSFS 2024 Flight Planner — Setup Guide

A full-featured preflight planning tool for Microsoft Flight Simulator 2024.
Covers route planning, weather, winds aloft, NOTAMs, fuel planning, and flight logging.

---

## Requirements

- Python 3.11 or higher (tested on 3.14)
- Microsoft Flight Simulator 2024 (for .pln export auto-copy)
- An internet connection (for live weather, NOTAMs, winds aloft)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/msfs-flightplanner.git
cd msfs-flightplanner
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Then open `.env` in a text editor and add your values (see section below).

### 5. Download the airport database

On first run the app will automatically download and build the airport database
from OurAirports (free, ~200MB download, builds a local airports.db).
This takes about 30–60 seconds and only happens once.

### 6. Run the app

```bash
python gui.py
```

---

## Environment Variables

These go in your `.env` file in the project root.
**Never commit your `.env` file to Git.**

### `CHECKWX_API_KEY` — Required for global METAR/TAF coverage

The app uses the FAA Aviation Weather Center (AWC) as the primary weather source —
this works worldwide with no key required.

CheckWX is the fallback for airports where AWC returns no data (common outside the US).
Without it the app still works, but weather may be missing for some international airports.

**How to get it (free, takes 30 seconds):**
1. Go to https://www.checkwxapi.com
2. Sign up — no credit card required
3. Copy your API key from the dashboard
4. Add to `.env`:

```
CHECKWX_API_KEY=your_key_here
```

---

## Optional Services

These are not required. The app works fully without them.

### Navigraph Charts

Navigraph chart links are deeplinks that open in the Navigraph Charts web app
or desktop app. They require an active **Navigraph subscription**.

- No API key needed in this app
- Just make sure you are signed in at https://navigraph.com before clicking chart links

### FAA NOTAM API (official)

NOTAMs work out of the box using the FAA public search endpoint — no key needed.

If you want to use the official FAA API instead (higher rate limits, structured data):
1. Register at https://api.faa.gov/s/
2. Sign in with your login.gov account
3. Go to My Apps → Add New App
4. Request access to the NOTAM API (approval takes 24–48 hours)
5. Once approved, enter your `client_id` and `client_secret` directly
   in the **NOTAM API** fields at the bottom of the left panel in the app
   (these are entered at runtime, not stored in `.env`)

### SimBrief

SimBrief integration uses your SimBrief **Pilot ID** (a number, not a password).
Enter it in the SimBrief field in the app when prompted.
You can find your Pilot ID at https://www.simbrief.com → Account settings.

---

## Features

| Feature | Source | Auth required |
|---|---|---|
| METAR / TAF | FAA AWC + CheckWX fallback | No (CheckWX key optional) |
| Winds aloft | FAA Aviation Weather Center | No |
| NOTAMs | FAA public search + Autorouter fallback | No |
| Airport database | OurAirports (auto-download) | No |
| Navigraph charts | Navigraph deeplinks | Navigraph subscription |
| SimBrief OFP | SimBrief API | Free SimBrief account |
| FAA NOTAM API | api.faa.gov | Optional FAA registration |

---

## Generating requirements.txt

If `requirements.txt` is missing, generate it from your venv:

```bash
pip freeze > requirements.txt
```

---

## Project Structure

```
gui.py           — Main GUI application (customtkinter)
aircraft.py      — Aircraft profiles and performance data
airport_db.py    — OurAirports database management
alternate.py     — IFR alternate airport selection
cruise_alt.py    — Hemispherical cruise altitude (FAR 91.159/91.179)
destination.py   — Destination picker logic
flightplan.py    — Flight plan builder and .pln export
fuel_plan.py     — POH-based fuel planning
logbook.py       — SQLite flight logbook
main.py          — CLI entry point (optional, GUI is primary)
metar.py         — METAR/TAF fetcher (AWC + CheckWX)
navigraph.py     — Navigraph chart deeplinks
notams.py        — NOTAM fetcher (FAA public + Autorouter)
poh_data.py      — POH performance tables for all aircraft
simbrief.py      — SimBrief API integration
view_logbook.py  — Logbook viewer helper
winds_aloft.py   — AWC winds aloft (FD winds parser + interpolation)
```

---

## Notes

- Flight plans are exported as `.pln` files and automatically copied to your
  MSFS Community folder if the standard installation path is detected.
- The logbook is stored locally in `logbook.db` — back it up if you care about it.
- All weather data is for **simulation purposes only**.
  Always use official sources for real-world flight planning.