import json
from pathlib import Path

STATIONS_FILE = Path(__file__).resolve().parent / "data" / "stations.json"


def find_station(keyword):
    if not keyword:
        return []

    try:
        with STATIONS_FILE.open("r", encoding="utf-8") as f:
            stations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    keyword = keyword.strip().lower()
    matches = []
    for station in stations:
        name = str(station.get("STATION_NM", ""))
        if keyword in name.lower():
            matches.append(station)

    return matches[:5]
