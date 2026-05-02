import requests

from config import BUS_API_KEY

ENDPOINT = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2"


class BusAPIError(Exception):
    pass


def get_bus_arrival(station_id: str):
    if not BUS_API_KEY:
        raise BusAPIError("BUS_API_KEY is missing. Please set it in .env")

    params = {
        "serviceKey": BUS_API_KEY,
        "stationId": station_id,
        "format": "json",
    }

    try:
        response = requests.get(ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise BusAPIError(f"HTTP error: {e}") from e

    try:
        payload = response.json()
        bus_list = payload["response"]["msgBody"].get("busArrivalList", [])
    except (ValueError, KeyError, TypeError) as e:
        raise BusAPIError(f"JSON parsing error: {e}") from e

    if not isinstance(bus_list, list):
        return []

    results = []
    for item in bus_list:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "route": item.get("routeName"),
                "time1": item.get("predictTime1"),
                "time2": item.get("predictTime2"),
            }
        )

    return results
