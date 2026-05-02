import json
from pathlib import Path
from typing import Dict, List


DATA_PATH = Path(__file__).resolve().parent / "data" / "stations.json"


def _load_stations() -> List[Dict[str, str]]:
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def find_station(keyword: str) -> List[Dict[str, str]]:
    if not keyword:
        return []

    stations = _load_stations()
    keyword_lower = keyword.strip().lower()

    matches = [
        station
        for station in stations
        if isinstance(station, dict)
        and keyword_lower in str(station.get("STATION_NM", "")).lower()
    ]

    return matches[:5]
