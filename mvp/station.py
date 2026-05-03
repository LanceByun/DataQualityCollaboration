import json
from pathlib import Path

STATIONS_FILE = Path(__file__).resolve().parent / "data" / "stations.json"


def load_stations():
    with STATIONS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        return []
    return data


def find_station(keyword, stations):
    keyword = (keyword or "").strip().lower()
    if not keyword:
        return []

    matches = []
    for station in stations:
        station_name = str(station.get("STATION_NM", ""))
        if keyword in station_name.lower():
            matches.append(station)

    return matches[:5]
