# ============================================================
# MSFS 2024 Flight Planner — GUI
# Built with customtkinter (modern tkinter wrapper)
# ============================================================

import os
import re
import threading
import webbrowser
from datetime import datetime, timezone
from dotenv import load_dotenv

import customtkinter as ctk
from tkinter import messagebox

from airport_db import AirportDB
from aircraft import AIRCRAFT_PROFILES, estimate_flight_time
from metar import get_metar, parse_flight_category, get_enroute_metars
from destination import (
    _filter_by_runway, _score_candidates,
)
from aircraft import nm_range_for_hours
from alternate import alternate_required, find_alternate
from simbrief import build_dispatch_url
from navigraph import build_airport_chart_url
from flightplan import export_pln, copy_to_msfs
from logbook import log_flight, display_totals
from geopy.distance import geodesic

load_dotenv()

# ── App theme ─────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CAT_COLORS = {
    "VFR":  "#22c55e",   # green
    "MVFR": "#eab308",   # yellow
    "IFR":  "#ef4444",   # red
    "LIFR": "#a855f7",   # purple
    "UNKN": "#94a3b8",   # grey
}


# ── Main Application ──────────────────────────────────────────

class FlightPlannerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("MSFS 2024 Flight Planner")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # State
        self.db           = None
        self.aircraft     = None
        self.dep               = None
        self.arr               = None
        self.fuel_plan         = None
        self.fuel_plan_wind    = None
        self.route_winds       = []
        self.notam_client_id     = ""
        self.notam_client_secret = ""

        self.alt_airport  = None
        self.dep_metar    = None
        self.arr_metar    = None
        self.dist_nm      = 0.0
        self.ftime        = ""
        self.pln_rules    = "VFR"
        self.dispatch_url = None
        self.pln_file     = None

        self._build_ui()
        self._load_db()

    # ── UI Construction ───────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left panel ───────────────────────────────────────
        self.left = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.left.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.left.grid_propagate(False)
        self._build_left_panel()

        # ── Right panel ──────────────────────────────────────
        self.right = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.right.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.right.grid_columnconfigure(0, weight=1)
        self._build_right_panel()

        # ── Status bar ───────────────────────────────────────
        self.status_var = ctk.StringVar(value="Loading airport database...")
        self.status_bar = ctk.CTkLabel(
            self, textvariable=self.status_var,
            anchor="w", height=28,
            fg_color=("#e2e8f0", "#1e293b"),
            text_color=("#64748b", "#94a3b8"),
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _build_left_panel(self):
        p = self.left
        pad = {"padx": 16, "pady": 6}

        # Title
        ctk.CTkLabel(
            p, text="✈  Flight Planner",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 4), **{"padx": 16})

        ctk.CTkLabel(
            p, text="MSFS 2024",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60"),
        ).pack(pady=(0, 16), **{"padx": 16})

        self._section_label(p, "AIRCRAFT")

        # Aircraft dropdown
        ac_labels = [v["label"] for v in AIRCRAFT_PROFILES.values()]
        self.ac_var = ctk.StringVar(value=ac_labels[4])  # SR22 default
        self.ac_menu = ctk.CTkOptionMenu(
            p, variable=self.ac_var,
            values=ac_labels,
            width=248,
            command=self._on_aircraft_change,
        )
        self.ac_menu.pack(**pad)

        self.ac_info = ctk.CTkLabel(
            p, text="", font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            wraplength=240,
        )
        self.ac_info.pack(padx=16, pady=(0, 8))
        self._on_aircraft_change(self.ac_var.get())

        # ── Departure / Arrival ───────────────────────────────
        self._section_label(p, "ROUTE")

        ctk.CTkLabel(p, text="Departure ICAO", anchor="w").pack(fill="x", padx=16)
        self.dep_entry = ctk.CTkEntry(p, placeholder_text="e.g. KDFW", width=248)
        self.dep_entry.pack(**pad)
        self.dep_entry.bind("<FocusOut>", lambda e: self._lookup_airport("dep"))
        self.dep_entry.bind("<Return>",   lambda e: self._lookup_airport("dep"))

        ctk.CTkLabel(p, text="Arrival ICAO", anchor="w").pack(fill="x", padx=16)
        self.arr_entry = ctk.CTkEntry(p, placeholder_text="e.g. KATL or leave blank", width=248)
        self.arr_entry.pack(**pad)
        self.arr_entry.bind("<FocusOut>", lambda e: self._lookup_airport("arr"))
        self.arr_entry.bind("<Return>",   lambda e: self._lookup_airport("arr"))

        # ── Flight rules ──────────────────────────────────────
        self._section_label(p, "FLIGHT RULES")

        self.fr_var = ctk.StringVar(value="VFR")
        fr_frame = ctk.CTkFrame(p, fg_color="transparent")
        fr_frame.pack(fill="x", padx=16, pady=4)
        ctk.CTkRadioButton(
            fr_frame, text="VFR", variable=self.fr_var, value="VFR",
            command=self._on_fr_change,
        ).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(
            fr_frame, text="IFR", variable=self.fr_var, value="IFR",
            command=self._on_fr_change,
        ).pack(side="left")

        # ── Duration slider ───────────────────────────────────
        self._section_label(p, "TARGET DURATION")

        self.dur_var = ctk.DoubleVar(value=2.0)
        self.dur_label = ctk.CTkLabel(p, text="2.0 hours", font=ctk.CTkFont(size=12))
        self.dur_label.pack(padx=16)
        self.dur_slider = ctk.CTkSlider(
            p, from_=0.5, to=6.0, number_of_steps=22,
            variable=self.dur_var, width=248,
            command=self._on_duration_change,
        )
        self.dur_slider.pack(padx=16, pady=(0, 16))

        # ── Action buttons ────────────────────────────────────
        self._section_label(p, "PLAN")

        self.btn_find = ctk.CTkButton(
            p, text="🔍  Find Destination",
            width=248, height=40,
            command=self._find_destination,
        )
        self.btn_find.pack(**pad)

        self.btn_surprise = ctk.CTkButton(
            p, text="🎲  Surprise Me!",
            width=248, height=40,
            fg_color="#7c3aed", hover_color="#6d28d9",
            command=self._surprise_destination,
        )
        self.btn_surprise.pack(**pad)

        self.btn_weather = ctk.CTkButton(
            p, text="⛅  Refresh Weather",
            width=248, height=36,
            fg_color=("gray70", "gray30"),
            command=self._refresh_weather,
        )
        self.btn_weather.pack(padx=16, pady=(4, 2))

        # Appearance toggle
        # ── NOTAM API credentials ───
        self._section_label(p, "NOTAM API (optional)")
        ctk.CTkLabel(p, text="client_id", anchor="w",
                     font=ctk.CTkFont(size=11)).pack(fill="x", padx=16)
        self.notam_id_entry = ctk.CTkEntry(
            p, placeholder_text="FAA client_id", width=248,
            font=ctk.CTkFont(size=11))
        self.notam_id_entry.pack(padx=16, pady=(0, 4))
        ctk.CTkLabel(p, text="client_secret", anchor="w",
                     font=ctk.CTkFont(size=11)).pack(fill="x", padx=16)
        self.notam_secret_entry = ctk.CTkEntry(
            p, placeholder_text="FAA client_secret", width=248,
            show="*", font=ctk.CTkFont(size=11))
        self.notam_secret_entry.pack(padx=16, pady=(0, 2))
        ctk.CTkLabel(
            p, text="Get free key: api.faa.gov/s/",
            font=ctk.CTkFont(size=10),
            text_color=("gray50","gray60"),
        ).pack(padx=16, pady=(0, 8))

        self.theme_btn = ctk.CTkButton(
            p, text="☀ Light Mode",
            width=248, height=30,
            fg_color="transparent",
            text_color=("gray50", "gray60"),
            hover_color=("gray85", "gray25"),
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="bottom", padx=16, pady=16)

    def _build_right_panel(self):
        p = self.right

        # ── Route card ────────────────────────────────────────
        self.route_card = self._card(p, "Route")
        self.route_label = ctk.CTkLabel(
            self.route_card,
            text="Select aircraft and enter departure ICAO to begin.",
            font=ctk.CTkFont(size=13),
            wraplength=600, justify="left",
        )
        self.route_label.pack(padx=16, pady=12, anchor="w")

        # ── Weather card ──────────────────────────────────────
        self.wx_card = self._card(p, "Weather")
        self.wx_frame = ctk.CTkFrame(self.wx_card, fg_color="transparent")
        self.wx_frame.pack(fill="x", padx=16, pady=8)
        self.wx_label = ctk.CTkLabel(
            self.wx_frame,
            text="No weather data yet.",
            font=ctk.CTkFont(size=12),
            justify="left",
        )
        self.wx_label.pack(anchor="w")

        # ── Alternate card ────────────────────────────────────
        self.alt_card = self._card(p, "Alternate Airport")
        self.alt_label = ctk.CTkLabel(
            self.alt_card,
            text="No alternate computed yet.",
            font=ctk.CTkFont(size=12),
            justify="left",
        )
        self.alt_label.pack(padx=16, pady=12, anchor="w")

        # ── Action buttons row ────────────────────────────────
        self.action_card = self._card(p, "Actions")
        btn_frame = ctk.CTkFrame(self.action_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=12)

        self.btn_simbrief = ctk.CTkButton(
            btn_frame, text="📋  Open SimBrief",
            width=160, height=38,
            command=self._open_simbrief,
            state="disabled",
        )
        self.btn_simbrief.pack(side="left", padx=(0, 8))

        self.btn_charts = ctk.CTkButton(
            btn_frame, text="📐  DEP Charts",
            width=140, height=38,
            fg_color=("#0ea5e9", "#0284c7"),
            command=self._open_charts_dep,
            state="disabled",
        )
        self.btn_charts.pack(side="left", padx=(0, 8))

        self.btn_arr_charts = ctk.CTkButton(
            btn_frame, text="📐  ARR Charts",
            width=140, height=38,
            fg_color=("#0ea5e9", "#0284c7"),
            command=self._open_charts_arr,
            state="disabled",
        )
        self.btn_arr_charts.pack(side="left", padx=(0, 8))

        self.btn_export = ctk.CTkButton(
            btn_frame, text="💾  Export .pln",
            width=130, height=38,
            fg_color=("#16a34a", "#15803d"),
            command=self._export_pln,
            state="disabled",
        )
        self.btn_export.pack(side="left", padx=(0, 8))

        self.btn_fuel = ctk.CTkButton(
            btn_frame, text="⛽  Fuel Detail",
            width=130, height=38,
            fg_color=("#ea580c", "#c2410c"),
            command=self._show_fuel_detail,
            state="disabled",
        )
        self.btn_fuel.pack(side="left", padx=(0, 8))

        self.btn_winds = ctk.CTkButton(
            btn_frame,
            text="🌬  Winds",
            width=130,
            height=38,
            fg_color="#1a6b8a",
            hover_color="#14546e",
            state="disabled",
            command=self._show_winds_detail,
        )
        self.btn_winds.pack(side="left", padx=(0, 8))

        btn_frame2 = ctk.CTkFrame(self.action_card, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_log = ctk.CTkButton(
            btn_frame2, text="📓  Log Flight",
            width=160, height=38,
            fg_color=("#d97706", "#b45309"),
            command=self._log_flight,
            state="disabled",
        )
        self.btn_log.pack(side="left", padx=(0, 8))

        self.btn_logbook = ctk.CTkButton(
            btn_frame2, text="📊  View Logbook",
            width=160, height=38,
            fg_color=("gray70", "gray30"),
            command=self._view_logbook,
        )
        self.btn_logbook.pack(side="left", padx=(0, 8))

        self.btn_notams = ctk.CTkButton(
            btn_frame2, text="📋  NOTAMs",
            width=130, height=38,
            fg_color=("#b91c1c", "#991b1b"),
            hover_color=("#991b1b", "#7f1d1d"),
            state="disabled",
            command=self._show_notams,
        )
        self.btn_notams.pack(side="left", padx=(0, 8))

        # ── Logbook summary card ──────────────────────────────
        self.lb_card = self._card(p, "Logbook Totals")
        self.lb_label = ctk.CTkLabel(
            self.lb_card,
            text="No flights logged yet.",
            font=ctk.CTkFont(size=12),
            justify="left",
        )
        self.lb_label.pack(padx=16, pady=12, anchor="w")
        self._refresh_logbook_summary()

    # ── Helpers ───────────────────────────────────────────────

    def _section_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray50", "gray60"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 2))

    def _card(self, parent, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(10, 0))
        ctk.CTkFrame(frame, height=1, fg_color=("gray80", "gray30")).pack(
            fill="x", padx=16, pady=(4, 0)
        )
        return frame

    def _status(self, msg: str):
        self.status_var.set(f"  {msg}")

    def _get_aircraft(self):
        label = self.ac_var.get()
        for ac in AIRCRAFT_PROFILES.values():
            if ac["label"] == label:
                return ac
        return list(AIRCRAFT_PROFILES.values())[0]

    # ── Event handlers ────────────────────────────────────────

    def _load_db(self):
        def _load():
            self.db = AirportDB("data/airports.csv", "data/runways.csv")
            self._status("Ready — 22,479 airports loaded.")
        threading.Thread(target=_load, daemon=True).start()

    def _on_aircraft_change(self, label):
        ac = self._get_aircraft()
        self.ac_info.configure(
            text=f"{ac['developer']}  |  {ac['cruise_kts']}kt  FL{ac['cruise_alt']//100}"
        )

    def _on_duration_change(self, val):
        self.dur_label.configure(text=f"{float(val):.1f} hours")

    def _on_fr_change(self):
        self.pln_rules = self.fr_var.get()

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Dark Mode")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀ Light Mode")

    def _lookup_airport(self, which: str):
        if not self.db:
            return
        entry = self.dep_entry if which == "dep" else self.arr_entry
        icao = entry.get().strip().upper()
        if not icao:
            return
        ap = self.db.get_airport(icao)
        if ap:
            if which == "dep":
                self.dep = ap
                self._status(f"Departure: {ap['icao_code']} — {ap['name']}")
            else:
                self.arr = ap
                self._status(f"Arrival: {ap['icao_code']} — {ap['name']}")
            entry.configure(border_color=("#22c55e", "#16a34a"))
        else:
            entry.configure(border_color=("#ef4444", "#dc2626"))
            self._status(f"Airport {icao!r} not found.")

    # ── Flight planning ───────────────────────────────────────

    def _find_destination(self):
        if not self.db:
            self._status("Database still loading...")
            return
        dep_icao = self.dep_entry.get().strip().upper()
        if not dep_icao:
            self._status("Enter a departure ICAO first.")
            return
        self.dep = self.db.get_airport(dep_icao)
        if not self.dep:
            self._status(f"Departure {dep_icao!r} not found.")
            return

        ac = self._get_aircraft()
        hours = self.dur_var.get()
        self._status(f"Searching destinations {hours:.1f}h from {dep_icao}...")
        self.btn_find.configure(state="disabled", text="Searching...")

        def _search():
            from aircraft import nm_range_for_hours
            min_nm, max_nm = nm_range_for_hours(hours, ac)
            candidates = self.db.find_airports_in_range(
                dep_icao, min_nm, max_nm,
                airport_types=ac["type_filter"],
            )
            candidates = _filter_by_runway(candidates, self.db, ac["min_runway_ft"])
            if candidates.empty:
                self.after(0, lambda: self._status("No airports found in range."))
                self.after(0, lambda: self.btn_find.configure(
                    state="normal", text="🔍  Find Destination"))
                return
            scored = _score_candidates(candidates)
            top = scored.head(10)
            self.after(0, lambda: self._show_destination_picker(top, ac))
            self.after(0, lambda: self.btn_find.configure(
                state="normal", text="🔍  Find Destination"))

        threading.Thread(target=_search, daemon=True).start()

    def _surprise_destination(self):
        if not self.db:
            self._status("Database still loading...")
            return
        dep_icao = self.dep_entry.get().strip().upper()
        if not dep_icao:
            self._status("Enter a departure ICAO first.")
            return
        self.dep = self.db.get_airport(dep_icao)
        if not self.dep:
            self._status(f"Departure {dep_icao!r} not found.")
            return

        ac = self._get_aircraft()
        hours = self.dur_var.get()
        self._status(f"Finding surprise destination...")
        self.btn_surprise.configure(state="disabled", text="Searching...")

        def _search():
            from aircraft import nm_range_for_hours
            min_nm, max_nm = nm_range_for_hours(hours, ac)
            candidates = self.db.find_airports_in_range(
                dep_icao, min_nm, max_nm,
                airport_types=ac["type_filter"],
            )
            candidates = _filter_by_runway(candidates, self.db, ac["min_runway_ft"])
            if candidates.empty:
                self.after(0, lambda: self._status("No airports found."))
                self.after(0, lambda: self.btn_surprise.configure(
                    state="normal", text="🎲  Surprise Me!"))
                return
            scored = _score_candidates(candidates)
            top_pool = scored.head(max(10, len(scored) // 3))
            chosen = top_pool.sample(1).iloc[0].to_dict()
            self.after(0, lambda: self._select_destination(chosen, ac))
            self.after(0, lambda: self.btn_surprise.configure(
                state="normal", text="🎲  Surprise Me!"))

        threading.Thread(target=_search, daemon=True).start()

    def _show_destination_picker(self, candidates, ac):
        """Open a popup to pick from candidate destinations."""
        win = ctk.CTkToplevel(self)
        win.title("Select Destination")
        win.geometry("700x420")
        win.grab_set()

        ctk.CTkLabel(
            win, text="Select Destination Airport",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(16, 8))

        frame = ctk.CTkScrollableFrame(win)
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        for i, (_, row) in enumerate(candidates.iterrows()):
            ftime = estimate_flight_time(row["dist_nm"], ac)
            btn = ctk.CTkButton(
                frame,
                text=(
                    f"{row['icao_code']}  —  {row['name'][:35]}\n"
                    f"{row['iso_country']}  |  {row['type'].replace('_airport','')}  |  "
                    f"{row['dist_nm']:.0f} NM  |  {ftime}"
                ),
                anchor="w",
                height=52,
                font=ctk.CTkFont(size=12),
                command=lambda r=row.to_dict(), w=win, a=ac: (
                    w.destroy(), self._select_destination(r, a)
                ),
            )
            btn.pack(fill="x", pady=3)

        ctk.CTkButton(
            win, text="Cancel", fg_color="transparent",
            command=win.destroy,
        ).pack(pady=8)

    def _select_destination(self, row: dict, ac: dict):
        """Set arrival airport and trigger full planning."""
        self.arr = self.db.get_airport(row["icao_code"])
        if not self.arr:
            self._status(f"Could not load {row['icao_code']}")
            return

        self.arr_entry.delete(0, "end")
        self.arr_entry.insert(0, row["icao_code"])
        self.arr_entry.configure(border_color=("#22c55e", "#16a34a"))

        self.aircraft = ac
        self.dist_nm = geodesic(
            (self.dep["latitude_deg"], self.dep["longitude_deg"]),
            (self.arr["latitude_deg"], self.arr["longitude_deg"])
        ).nautical
        self.ftime = estimate_flight_time(self.dist_nm, ac)
        self.pln_rules = self.fr_var.get()

        self._update_route_card()
        self._refresh_weather()

    def _refresh_weather(self):
        if not self.dep or not self.arr:
            self._status("Set departure and arrival first.")
            return
        self._status("Fetching weather...")
        self.wx_label.configure(text="Fetching weather data...")

        def _fetch():
            self.dep_metar = get_metar(self.dep["icao_code"])
            self.arr_metar = get_metar(self.arr["icao_code"])
            try:
                self.enroute  = get_enroute_metars(
                    self.dep["icao_code"], self.arr["icao_code"], self.db
                )
            except Exception:
                self.enroute = []
            self.after(0, self._update_weather_card)
            self.after(0, self._compute_alternate)
            self.after(500, self._fetch_winds_async)

        threading.Thread(target=_fetch, daemon=True).start()

    def _compute_alternate(self):
        if not self.arr_metar or alternate_required(self.arr_metar):
            self._status("Computing alternate...")

            def _find():
                self.alt_airport = None
                if alternate_required(self.arr_metar):
                    candidates = self.db.find_airports_in_range(
                        self.arr["icao_code"], 30, 200,
                        airport_types=["large_airport", "medium_airport"],
                    )
                    from alternate import (
                        _filter_by_runway as alt_filter,
                        _fetch_metars_safe, _score_alternates
                    )
                    candidates = alt_filter(
                        candidates, self.db, self.aircraft["min_runway_ft"]
                    )
                    if not candidates.empty:
                        top = candidates.head(15)
                        metars = _fetch_metars_safe(top["icao_code"].tolist())
                        scored = _score_alternates(top, metars, self.arr_metar)
                        if not scored.empty:
                            self.alt_airport = scored.iloc[0].to_dict()
                self.after(0, self._update_alternate_card)

            threading.Thread(target=_find, daemon=True).start()
        else:
            self.alt_airport = None
            self._update_alternate_card()

    # ── Card updaters ─────────────────────────────────────────

    def _update_route_card(self):
        if not self.dep or not self.arr:
            return

        from cruise_alt import suggest_cruise_alt
        ac = self._get_aircraft()
        self.alt_suggestion = suggest_cruise_alt(
            self.dep, self.arr, ac, self.pln_rules
        )

        course  = self.alt_suggestion["course_deg"]
        direct  = self.alt_suggestion["direction"]
        options = self.alt_suggestion["options"]
        default = self.alt_suggestion["default"]

        self.selected_cruise_alt = default["ft"]

        if self.pln_rules == "VFR":
            hemi = ("Odd+500ft" if direct == "EAST" else "Even+500ft") + " altitudes (VFR)"
        else:
            hemi = ("Odd FLs" if direct == "EAST" else "Even FLs") + " (IFR)"

        dep_id = self.dep["icao_code"]
        arr_id = self.arr["icao_code"]
        text = (
            f"{dep_id}  ->  {arr_id}\n"
            f"Distance : {self.dist_nm:.0f} NM     Est. time: {self.ftime}     Rules: {self.pln_rules}\n"
            f"Course   : {course:.0f} deg  ({direct}bound) - {hemi}"
        )
        self.route_label.configure(text=text)

        for widget in self.route_card.winfo_children():
            if getattr(widget, "_is_alt_selector", False):
                widget.destroy()

        alt_frame = ctk.CTkFrame(self.route_card, fg_color="transparent")
        alt_frame._is_alt_selector = True
        alt_frame.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(alt_frame, text="Cruise Altitude:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))

        alt_labels = [o["label"] for o in options]
        self.alt_var = ctk.StringVar(value=default["label"])
        alt_menu = ctk.CTkOptionMenu(alt_frame, variable=self.alt_var, values=alt_labels, width=220, command=self._on_alt_change)
        alt_menu.pack(side="left")

        direction_color = "#22c55e" if direct == "EAST" else "#f97316"
        ctk.CTkLabel(alt_frame, text=f"  {direct}bound  {course:.0f} deg", text_color=direction_color, font=ctk.CTkFont(size=12)).pack(side="left", padx=10)

    def _on_alt_change(self, label: str):
        if not hasattr(self, "alt_suggestion"):
            return
        for o in self.alt_suggestion["options"]:
            if o["label"] == label:
                self.selected_cruise_alt = o["ft"]
                break

    # ── Card updaters (continued) ─────────────────────────────

    def _update_weather_card(self):
        lines = []

        for label, metar, icao in [
            ("DEP", self.dep_metar, self.dep["icao_code"] if self.dep else ""),
            ("ARR", self.arr_metar, self.arr["icao_code"] if self.arr else ""),
        ]:
            if metar:
                cat   = parse_flight_category(metar)
                color = CAT_COLORS.get(cat, "#94a3b8")
                raw   = metar.get("rawOb", "N/A")[:60]
                wind  = f"{metar.get('wdir','---')}°/{metar.get('wspd','---')}kt"
                vis   = metar.get("visib", "---")
                temp  = metar.get("temp", "---")
                lines.append(
                    f"[{label}] {icao}  ►  {cat}  |  {wind}  Vis:{vis}SM  Temp:{temp}°C\n"
                    f"       {raw}"
                )
            else:
                lines.append(f"[{label}] {icao}  ►  No METAR available")

        if hasattr(self, "enroute") and self.enroute:
            lines.append("\nEnroute:")
            for m in self.enroute:
                cat = parse_flight_category(m)
                lines.append(
                    f"  {m.get('icaoId','?')}  ►  {cat}  |  {m.get('rawOb','')[:50]}"
                )

        cats = []
        for m in [self.dep_metar, self.arr_metar]:
            if m:
                cats.append(parse_flight_category(m))
        if cats:
            order = ["VFR", "MVFR", "IFR", "LIFR"]
            worst = max(cats, key=lambda c: order.index(c) if c in order else 0)
            suggested = "IFR" if worst in ("IFR", "LIFR", "MVFR") else "VFR"
            lines.append(f"\nWeather suggests: {suggested}")
            self.fr_var.set(suggested)
            self.pln_rules = suggested

        self.wx_label.configure(text="\n".join(lines))
        self._status("Weather updated.")
        self._enable_action_buttons()

    def _update_alternate_card(self):
        if self.alt_airport:
            alt  = self.alt_airport
            metar = alt.get("alt_metar")
            cat   = parse_flight_category(metar) if metar else "N/A"
            text  = (
                f"REQUIRED — Destination below alternate minima\n\n"
                f"{alt['icao_code']}  —  {alt['name']}\n"
                f"Distance: {alt['dist_nm']:.0f} NM from destination  |  Weather: {cat}"
            )
        elif self.arr_metar and not alternate_required(self.arr_metar):
            text = "NOT REQUIRED — Destination weather above 2000ft / 3SM"
        else:
            text = "No alternate computed."

        self.alt_label.configure(text=text)
        self._build_simbrief_url()
        self._status("Ready.")

    def _build_simbrief_url(self):
        if not self.dep or not self.arr:
            return
        user = os.getenv("SIMBRIEF_USERNAME", "").strip()
        if not user:
            return
        ac = self._get_aircraft()
        cruise = getattr(self, "selected_cruise_alt", ac["cruise_alt"])
        self.dispatch_url = build_dispatch_url(
            dep_icao      = self.dep["icao_code"],
            arr_icao      = self.arr["icao_code"],
            alt_icao      = self.alt_airport["icao_code"] if self.alt_airport else None,
            aircraft      = ac,
            simbrief_user = user,
            units         = "kgs",
            cruise_alt    = cruise,
        )

    def _enable_action_buttons(self):
        for btn in [
            self.btn_simbrief, self.btn_charts, self.btn_arr_charts,
            self.btn_export, self.btn_log, self.btn_fuel, self.btn_winds, self.btn_notams,
        ]:
            btn.configure(state="normal")

    def _refresh_logbook_summary(self):
        try:
            from logbook import init_db, _fmt_time
            import sqlite3
            init_db()
            with sqlite3.connect("logbook.db") as conn:
                conn.row_factory = sqlite3.Row
                t = conn.execute(
                    "SELECT * FROM totals_cache WHERE id = 1"
                ).fetchone()
            if t and t["flight_count"] > 0:
                text = (
                    f"Flights: {t['flight_count']}     "
                    f"Total: {_fmt_time(t['total_time'])}\n"
                    f"Day: {_fmt_time(t['day_time'])}     "
                    f"Night: {_fmt_time(t['night_time'])}\n"
                    f"IFR: {_fmt_time(t['ifr_time'])}     "
                    f"VFR: {_fmt_time(t['vfr_time'])}\n"
                    f"XC: {_fmt_time(t['xc_time'])}     "
                    f"SEL: {_fmt_time(t['sel_time'])}     "
                    f"Jet: {_fmt_time(t['jet_time'])}"
                )
                self.lb_label.configure(text=text)
        except Exception:
            pass

    # ── Action button handlers ────────────────────────────────

    def _open_simbrief(self):
        if self.dispatch_url:
            webbrowser.open(self.dispatch_url)
        else:
            self._status("No SimBrief URL — set SIMBRIEF_USERNAME in .env")

    def _open_charts_dep(self):
        if self.dep:
            webbrowser.open(build_airport_chart_url(self.dep["icao_code"], "DEP"))

    def _open_charts_arr(self):
        if self.arr:
            webbrowser.open(build_airport_chart_url(self.arr["icao_code"], "APR"))

    def _export_pln(self):
        if not self.dep or not self.arr:
            return
        ac = self._get_aircraft()
        cruise = getattr(self, "selected_cruise_alt", ac["cruise_alt"])
        pln_file = export_pln(
            dep          = self.dep,
            arr          = self.arr,
            aircraft     = ac,
            alt_airport  = self.alt_airport,
            flight_rules = self.pln_rules,
            cruise_alt   = cruise,
        )
        self.pln_file = pln_file
        copy_to_msfs(pln_file, type("C", (), {"print": lambda s, *a, **k: None})())
        messagebox.showinfo(
            "Flight Plan Exported",
            f"Saved to:\n{pln_file}\n\nCopied to MSFS Plans folder if found.",
        )
        self._status(f"Exported: {os.path.basename(pln_file)}")

    def _log_flight(self):
        if not self.dep or not self.arr:
            return
        ac = self._get_aircraft()
        match = re.match(r'(\d+)h\s*(\d+)m', self.ftime)
        block_hrs = (
            int(match.group(1)) + int(match.group(2)) / 60
            if match else self.dist_nm / ac["cruise_kts"]
        )
        from metar import parse_flight_category
        dep_cat = parse_flight_category(self.dep_metar) if self.dep_metar else ""
        arr_cat = parse_flight_category(self.arr_metar) if self.arr_metar else ""

        flight_id = log_flight(
            dep            = self.dep,
            arr            = self.arr,
            aircraft       = ac,
            block_time_hrs = block_hrs,
            flight_rules   = self.pln_rules,
            dist_nm        = self.dist_nm,
            alt_airport    = self.alt_airport,
            dep_conditions = dep_cat,
            arr_conditions = arr_cat,
        )
        self._refresh_logbook_summary()
        messagebox.showinfo(
            "Flight Logged",
            f"Flight #{flight_id} logged!\n"
            f"{self.dep['icao_code']} -> {self.arr['icao_code']}\n"
            f"{self.ftime}  |  {self.pln_rules}",
        )
        self._status(f"Flight #{flight_id} logged.")
        self.btn_log.configure(state="disabled", text="✓ Logged")

    def _view_logbook(self):
        from logbook import init_db, _fmt_time
        import sqlite3

        win = ctk.CTkToplevel(self)
        win.title("Pilot Logbook")
        win.geometry("1100x600")

        ctk.CTkLabel(
            win, text="✈  Pilot Logbook",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(16, 8))

        frame = ctk.CTkScrollableFrame(win)
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        init_db()
        with sqlite3.connect("logbook.db") as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM flights ORDER BY date DESC, id DESC LIMIT 100"
            ).fetchall()

        if not rows:
            ctk.CTkLabel(frame, text="No flights logged yet.").pack(pady=20)
            return

        headers = [
            ("Date", 100), ("From", 55), ("To", 55), ("Aircraft", 200),
            ("Cat", 45), ("Total", 55), ("Day", 55), ("Night", 55),
            ("IFR", 55), ("VFR", 55), ("XC", 55), ("NM", 50),
        ]
        hrow = ctk.CTkFrame(frame, fg_color=("gray80", "gray25"))
        hrow.pack(fill="x", pady=(0, 2))
        for title, w in headers:
            ctk.CTkLabel(
                hrow, text=title, width=w,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(side="left", padx=2)

        for row in rows:
            r = ctk.CTkFrame(frame, fg_color=("gray95", "gray20"), corner_radius=4)
            r.pack(fill="x", pady=1)
            vals = [
                (row["date"],                        100),
                (row["dep_icao"],                    55),
                (row["arr_icao"],                    55),
                (row["aircraft_label"][:28],         200),
                (row["aircraft_cat"],                45),
                (_fmt_time(row["total_time"]),       55),
                (_fmt_time(row["day_time"]),         55),
                (_fmt_time(row["night_time"]),       55),
                (_fmt_time(row["ifr_time"]),         55),
                (_fmt_time(row["vfr_time"]),         55),
                (_fmt_time(row["xc_time"]),          55),
                (str(int(row["dist_nm"] or 0)),      50),
            ]
            for val, w in vals:
                ctk.CTkLabel(r, text=val, width=w, font=ctk.CTkFont(size=11)).pack(
                    side="left", padx=2, pady=3
                )


    def _show_fuel_detail(self):
        """Open popup with full POH fuel breakdown."""
        from fuel_plan import compute_fuel_plan, format_fuel_plan

        # Always recompute fresh so aircraft changes are reflected
        fp = None
        if self.dep and self.arr:
            ac = self._get_aircraft()
            fp = compute_fuel_plan(
                dep          = self.dep,
                arr          = self.arr,
                aircraft     = ac,
                dist_nm      = getattr(self, "dist_nm", 0),
                cruise_fl    = getattr(self, "selected_cruise_alt", ac["cruise_alt"]) // 100,
                flight_rules = getattr(self, "pln_rules", "IFR"),
            )
            self.fuel_plan = fp

        # Close any existing fuel window before opening a new one
        existing = getattr(self, "_fuel_win", None)
        if existing and existing.winfo_exists():
            existing.destroy()

        # Keep a reference on self so the window isn't garbage-collected
        self._fuel_win = ctk.CTkToplevel(self)
        self._fuel_win.title("Fuel Plan Detail")
        self._fuel_win.geometry("640x560")
        self._fuel_win.attributes("-topmost", True)
        self._fuel_win.after(100, lambda: (
            self._fuel_win.attributes("-topmost", False),
            self._fuel_win.lift(),
            self._fuel_win.focus_force(),
        ))

        ctk.CTkLabel(
            self._fuel_win, text="⛽  Fuel Planning",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(16, 8))

        if not fp:
            ac = self._get_aircraft()
            code = ac.get("simbrief_code", "?")
            ctk.CTkLabel(
                self._fuel_win,
                text=(
                    f"No POH data for simbrief code: {code}\n\n"
                    f"Aircraft: {ac.get('label', '?')}\n\n"
                    f"Make sure poh_data.py is in the same folder\n"
                    f"and contains an entry for \"{code}\"."
                ),
                font=ctk.CTkFont(size=12),
                justify="center",
            ).pack(pady=20, padx=20)
            ctk.CTkButton(
                self._fuel_win, text="Close",
                command=self._fuel_win.destroy,
            ).pack(pady=(0, 12))
            return

        poh = fp["poh"]
        ctk.CTkLabel(
            self._fuel_win,
            text=f"{poh['label']}  —  Tier {poh['tier']} data",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        ).pack(padx=16)

        text_box = ctk.CTkTextbox(
            self._fuel_win,
            font=ctk.CTkFont(family="Courier", size=12),
        )
        text_box.pack(fill="both", expand=True, padx=16, pady=12)
        text_box.insert("1.0", format_fuel_plan(fp))
        text_box.configure(state="disabled")

        ctk.CTkButton(
            self._fuel_win, text="Close",
            command=self._fuel_win.destroy,
        ).pack(pady=(0, 12))


    # ── Winds Aloft ───────────────────────────────────────────────

    def _fetch_winds_async(self):
        """Start background thread to fetch winds aloft."""
        import threading
        if not self.dep or not self.arr:
            return
        t = threading.Thread(target=self._fetch_winds_worker, daemon=True)
        t.start()

    def _fetch_winds_worker(self):
        """Background worker: fetch winds then schedule UI update."""
        try:
            from winds_aloft import (
                fetch_route_winds, course_deg, wind_summary_line,
                adjust_fuel_plan_for_wind,
            )
            ac       = self._get_aircraft()
            fl       = getattr(self, "selected_cruise_alt", ac["cruise_alt"]) // 100
            wps      = getattr(self, "waypoints", [])
            course   = course_deg(self.dep, self.arr)

            self.route_winds = fetch_route_winds(self.dep, self.arr, wps, fl)

            # Pick midpoint wind for fuel adjustment
            mid_wind = None
            for rw in self.route_winds:
                if rw.get("wind") and rw.get("ident") not in (
                    self.dep.get("ident"), self.arr.get("ident")
                ):
                    mid_wind = rw["wind"]
                    break
            if not mid_wind and self.route_winds:
                mid_wind = self.route_winds[-1].get("wind")

            # Adjust fuel plan for wind
            if getattr(self, "fuel_plan", None) and mid_wind:
                self.fuel_plan_wind = adjust_fuel_plan_for_wind(
                    self.fuel_plan, mid_wind, course
                )
            else:
                self.fuel_plan_wind = self.fuel_plan

            # Build summary and schedule GUI update on main thread
            summary = wind_summary_line(self.route_winds, course)
            self.after(0, lambda s=summary: self._update_wind_ui(s))

        except Exception as e:
            self.after(0, lambda err=e: self._update_wind_ui(f"🌬  Wind data unavailable ({err})"))

    def _update_wind_ui(self, summary_text: str):
        """Update wind label on main thread."""
        if hasattr(self, "lbl_wind") and self.lbl_wind.winfo_exists():
            self.lbl_wind.configure(text=summary_text)

        # If fuel detail window is open, refresh it with wind-adjusted plan
        win = getattr(self, "_fuel_win", None)
        if win and win.winfo_exists():
            pass  # user can re-click for fresh data

    def _show_winds_detail(self):
        """Popup showing per-station winds along route."""
        from winds_aloft import headwind_component, course_deg as _course

        existing = getattr(self, "_winds_win", None)
        if existing and existing.winfo_exists():
            existing.destroy()

        self._winds_win = ctk.CTkToplevel(self)
        self._winds_win.title("Winds Aloft — Route Stations")
        self._winds_win.geometry("580x420")
        self._winds_win.attributes("-topmost", True)
        self._winds_win.after(100, lambda: (
            self._winds_win.attributes("-topmost", False),
            self._winds_win.lift(),
            self._winds_win.focus_force(),
        ))

        ctk.CTkLabel(
            self._winds_win, text="🌬  Winds Aloft — Route Stations",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(14, 4))

        if not self.route_winds:
            ctk.CTkLabel(
                self._winds_win,
                text="No wind data fetched yet.\nGenerate a route first.",
                font=ctk.CTkFont(size=12),
            ).pack(pady=20)
            ctk.CTkButton(
                self._winds_win, text="Close",
                command=self._winds_win.destroy,
            ).pack(pady=(0, 12))
            return

        course = _course(self.dep, self.arr) if self.dep and self.arr else 0

        tb = ctk.CTkTextbox(
            self._winds_win,
            font=ctk.CTkFont(family="Courier", size=12),
        )
        tb.pack(fill="both", expand=True, padx=14, pady=8)

        lines = [
            f"  {'STATION':<10} {'WIND':>9}  {'TEMP':>6}  {'HW/TW':>8}  NOTE",
            f"  {'─'*54}",
        ]
        for rw in self.route_winds:
            w    = rw.get("wind")
            ident = rw.get("ident", "?")
            stn   = w.get("station", "?") if w else "—"
            if not w:
                lines.append(f"  {ident:<10} {'no data':>9}")
                continue
            if w.get("variable"):
                wstr = "  VRB/LT "
                hw   = 0.0
            else:
                wstr = f"{w['dir']:03d}°/{w['speed_kt']:02d}kt"
                hw   = headwind_component(w["dir"], w["speed_kt"], course)
            temp  = f"{w.get('temp_c', 0):+d}°C"
            hwtag = f"HW +{hw:.0f}" if hw >= 0 else f"TW +{abs(hw):.0f}"
            lines.append(
                f"  {ident:<10} {wstr:>9}  {temp:>6}  {hwtag:>8}  stn:{stn}"
            )

        # Show wind-adjusted vs no-wind summary if available
        if hasattr(self, "fuel_plan_wind") and self.fuel_plan_wind:
            fp   = self.fuel_plan_wind
            unit = fp["unit"]
            gs   = fp.get("wind_gs", fp["cruise_ktas"])
            hw   = fp.get("wind_hw", 0)
            lines += [
                "",
                f"  {'─'*54}",
                f"  Course:   {course:.0f}°T",
                f"  TAS:      {fp['cruise_ktas']} kt",
                f"  GS:       {gs} kt  ({'HW' if hw>=0 else 'TW'} {abs(hw):.0f} kt)",
                f"  Block fuel (wind-adj): {fp['block_fuel']:.0f} {unit}",
                f"  ETE (wind-adj): {int(fp['total_time_hr'])}h {int((fp['total_time_hr']%1)*60):02d}m",
            ]

        tb.insert("1.0", "\n".join(lines))
        tb.configure(state="disabled")

        ctk.CTkButton(
            self._winds_win, text="Close",
            command=self._winds_win.destroy,
        ).pack(pady=(0, 12))

    # ── NOTAMs ────────────────────────────────────────────────

    def _show_notams(self):
        """Open NOTAMs popup for dep + arr airports."""
        existing = getattr(self, "_notams_win", None)
        if existing and existing.winfo_exists():
            existing.destroy()

        self._notams_win = ctk.CTkToplevel(self)
        self._notams_win.title("NOTAMs")
        self._notams_win.geometry("700x560")
        self._notams_win.attributes("-topmost", True)
        self._notams_win.after(100, lambda: (
            self._notams_win.attributes("-topmost", False),
            self._notams_win.lift(),
            self._notams_win.focus_force(),
        ))

        dep_id = self.dep["icao_code"] if self.dep else "?"
        arr_id = self.arr["icao_code"] if self.arr else "?"
        ctk.CTkLabel(
            self._notams_win,
            text=f"\U0001f4cb  NOTAMs \u2014 {dep_id} / {arr_id}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(14, 4))

        # Credentials are optional — public FAA endpoint works without them
        cid  = self.notam_id_entry.get().strip()
        csec = self.notam_secret_entry.get().strip()

        tb = ctk.CTkTextbox(
            self._notams_win,
            font=ctk.CTkFont(family="Courier", size=11),
        )
        tb.pack(fill="both", expand=True, padx=14, pady=8)
        tb.insert("1.0", "Fetching NOTAMs...\n")
        tb.configure(state="disabled")

        brow = ctk.CTkFrame(self._notams_win, fg_color="transparent")
        brow.pack(pady=(0, 12))
        ctk.CTkButton(brow, text="\U0001f504 Refresh",
                      command=lambda: self._fetch_notams_to_box(tb, cid, csec)
                      ).pack(side="left", padx=8)
        ctk.CTkButton(brow, text="Close",
                      command=self._notams_win.destroy
                      ).pack(side="left", padx=8)

        self._fetch_notams_to_box(tb, cid, csec)

    def _fetch_notams_to_box(self, tb, cid: str, csec: str):
        """Fetch NOTAMs in background and populate textbox."""
        import threading
        dep_icao = self.dep["icao_code"] if self.dep else ""
        arr_icao = self.arr["icao_code"] if self.arr else ""

        def _worker():
            from notams import fetch_route_notams, format_notams_text
            result = fetch_route_notams(dep_icao, arr_icao, cid, csec)
            text   = format_notams_text(result)
            self.after(0, lambda t=text: _update(t))

        def _update(text):
            if tb.winfo_exists():
                tb.configure(state="normal")
                tb.delete("1.0", "end")
                tb.insert("1.0", text)
                tb.configure(state="disabled")

        threading.Thread(target=_worker, daemon=True).start()

    def _show_fuel_detail(self):
        """Open popup with full POH fuel breakdown."""
        from fuel_plan import compute_fuel_plan, format_fuel_plan

        # Always recompute fresh so aircraft changes are reflected
        fp = None
        if self.dep and self.arr:
            ac = self._get_aircraft()
            fp = compute_fuel_plan(
                dep          = self.dep,
                arr          = self.arr,
                aircraft     = ac,
                dist_nm      = getattr(self, "dist_nm", 0),
                cruise_fl    = getattr(self, "selected_cruise_alt", ac["cruise_alt"]) // 100,
                flight_rules = getattr(self, "pln_rules", "IFR"),
            )
            self.fuel_plan = fp

        # Close any existing fuel window before opening a new one
        existing = getattr(self, "_fuel_win", None)
        if existing and existing.winfo_exists():
            existing.destroy()

        # Keep a reference on self so the window isn't garbage-collected
        self._fuel_win = ctk.CTkToplevel(self)
        self._fuel_win.title("Fuel Plan Detail")
        self._fuel_win.geometry("640x560")
        self._fuel_win.attributes("-topmost", True)
        self._fuel_win.after(100, lambda: (
            self._fuel_win.attributes("-topmost", False),
            self._fuel_win.lift(),
            self._fuel_win.focus_force(),
        ))

        ctk.CTkLabel(
            self._fuel_win, text="⛽  Fuel Planning",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(16, 8))

        if not fp:
            ac = self._get_aircraft()
            code = ac.get("simbrief_code", "?")
            ctk.CTkLabel(
                self._fuel_win,
                text=(
                    f"No POH data for simbrief code: {code}\n\n"
                    f"Aircraft: {ac.get('label', '?')}\n\n"
                    f"Make sure poh_data.py is in the same folder\n"
                    f"and contains an entry for \"{code}\"."
                ),
                font=ctk.CTkFont(size=12),
                justify="center",
            ).pack(pady=20, padx=20)
            ctk.CTkButton(
                self._fuel_win, text="Close",
                command=self._fuel_win.destroy,
            ).pack(pady=(0, 12))
            return

        poh = fp["poh"]
        ctk.CTkLabel(
            self._fuel_win,
            text=f"{poh['label']}  —  Tier {poh['tier']} data",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        ).pack(padx=16)

        text_box = ctk.CTkTextbox(
            self._fuel_win,
            font=ctk.CTkFont(family="Courier", size=12),
        )
        text_box.pack(fill="both", expand=True, padx=16, pady=12)
        text_box.insert("1.0", format_fuel_plan(fp))
        text_box.configure(state="disabled")

        ctk.CTkButton(
            self._fuel_win, text="Close",
            command=self._fuel_win.destroy,
        ).pack(pady=(0, 12))


# ── Entry point ───────────────────────────────────────────────

def main():
    app = FlightPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()