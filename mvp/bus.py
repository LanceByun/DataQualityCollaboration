import requests

from config import BUS_API_KEY

API_URL = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2"


def get_bus_arrival(station_id):
    if not BUS_API_KEY:
        raise RuntimeError("BUS_API_KEY is not set. Please add it to .env")

    params = {
        "serviceKey": BUS_API_KEY,
        "stationId": station_id,
        "format": "json",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"API failure: {e}")
    except ValueError:
        raise RuntimeError("API failure: invalid JSON response")

    try:
        bus_list = data["response"]["msgBody"]["busArrivalList"]
    except (KeyError, TypeError):
        return []

    results = []
    for item in bus_list:
        results.append(
            {
                "route": item.get("routeName"),
                "time1": item.get("predictTime1"),
                "time2": item.get("predictTime2"),
            }
        )

    return results
