import pandas as pd
from geopy.distance import geodesic

AMERICAS = {
    "US","CA","MX","BR","AR","CL","CO","PE","VE","EC","BO","PY","UY",
    "GY","SR","GF","PA","CR","NI","HN","GT","BZ","SV","CU","JM","HT",
    "DO","TT","BB","LC","VC","GD","AG","DM","KN","BS","TC","KY","VG",
    "VI","PR","AW","CW","BQ","SX","MF","GP","MQ"
}
EUROPE = {
    "GB","FR","DE","ES","IT","PT","NL","BE","CH","AT","SE","NO","DK",
    "FI","IE","PL","CZ","SK","HU","RO","BG","HR","SI","RS","BA","ME",
    "MK","AL","GR","CY","MT","LU","LI","MC","AD","SM","VA","IS","EE",
    "LV","LT","BY","UA","MD","TR","RU","GE","AM","AZ","KZ"
}
ALL_COUNTRIES = AMERICAS | EUROPE

VALID_TYPES = {"large_airport", "medium_airport", "small_airport"}
EXCLUDED_TYPES = {"closed", "balloonport", "seaplane_base", "heliport"}

class AirportDB:
    def __init__(self, airports_path="data/airports.csv", runways_path="data/runways.csv"):
        df = pd.read_csv(airports_path, low_memory=False)

        # Fill missing icao_code from ident when ident looks like a real ICAO (4 chars, letters/digits)
        mask_missing = df["icao_code"].isna()
        mask_ident_4 = df["ident"].str.match(r'^[A-Z0-9]{4}$', na=False)
        df.loc[mask_missing & mask_ident_4, "icao_code"] = df.loc[mask_missing & mask_ident_4, "ident"]

        self.airports = df[
            (df["iso_country"].isin(ALL_COUNTRIES)) &
            (df["icao_code"].notna()) &
            (df["icao_code"].str.len() == 4) &
            (df["type"].isin(VALID_TYPES))
        ].copy()

        self.runways = pd.read_csv(runways_path, low_memory=False)

        total = len(self.airports)
        by_type = self.airports["type"].value_counts().to_dict()
        print(f"[DB] Loaded {total} airports — {by_type}")

    def get_airport(self, icao: str):
        icao = icao.upper()
        match = self.airports[self.airports["icao_code"] == icao]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def find_airports_in_range(self, icao: str, min_nm: float, max_nm: float, airport_types=None):
        origin = self.get_airport(icao)
        if not origin:
            raise ValueError(f"Airport {icao} not found.")
        origin_coords = (origin["latitude_deg"], origin["longitude_deg"])
        candidates = self.airports.copy()
        if airport_types:
            candidates = candidates[candidates["type"].isin(airport_types)]

        # Vectorized distance calculation — much faster than row-by-row apply
        from math import radians, cos, sin, asin, sqrt
        lat1, lon1 = map(radians, origin_coords)
        lats = candidates["latitude_deg"].apply(radians)
        lons = candidates["longitude_deg"].apply(radians)
        dlat = lats - lat1
        dlon = lons - lon1
        a = dlat.apply(lambda x: sin(x/2)**2) + cos(lat1) * lats.apply(cos) * dlon.apply(lambda x: sin(x/2)**2)
        dist_nm = a.apply(lambda x: 2 * asin(sqrt(x))) * 3440.065  # Earth radius in NM
        candidates = candidates.copy()
        candidates["dist_nm"] = dist_nm
        result = candidates[(candidates["dist_nm"] >= min_nm) & (candidates["dist_nm"] <= max_nm)]
        return result.sort_values("dist_nm")

    def get_runways(self, icao: str):
        return self.runways[self.runways["airport_ident"] == icao]