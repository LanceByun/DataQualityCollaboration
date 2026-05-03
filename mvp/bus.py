import requests

from config import BUS_API_KEY

API_URL = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2"


def get_bus_arrival(station_id):
    params = {
        "serviceKey": BUS_API_KEY,
        "stationId": station_id,
        "format": "json",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise RuntimeError(f"API request failure: {error}") from error
    except ValueError as error:
        raise RuntimeError(f"API response JSON parse failure: {error}") from error

    try:
        bus_list = payload["response"]["msgBody"]["busArrivalList"]
    except (KeyError, TypeError) as error:
        raise RuntimeError(f"API response format error: {error}") from error

    if not isinstance(bus_list, list):
        return []

    result = []
    for bus in bus_list:
        result.append(
            {
                "route": bus.get("routeName"),
                "time1": bus.get("predictTime1"),
                "time2": bus.get("predictTime2"),
            }
        )
    return result
