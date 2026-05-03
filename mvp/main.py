from bus import get_bus_arrival
from station import find_station, load_stations


def main():
    try:
        stations = load_stations()
    except FileNotFoundError:
        print("stations.json 파일을 찾을 수 없습니다.")
        return
    except ValueError:
        print("stations.json 형식이 올바르지 않습니다.")
        return

    keyword = input("정류장 이름을 입력하세요: ").strip()
    matched = find_station(keyword, stations)

    if not matched:
        print("정류장을 찾을 수 없습니다.")
        return

    for idx, station in enumerate(matched, start=1):
        print(f"{idx}. {station.get('STATION_NM', '')}")

    selection = input("번호를 선택하세요: ").strip()
    if not selection.isdigit():
        print("잘못된 입력입니다. 숫자를 입력하세요.")
        return

    selected_index = int(selection) - 1
    if selected_index < 0 or selected_index >= len(matched):
        print("잘못된 선택입니다.")
        return

    station_id = matched[selected_index].get("STATION_ID")
    if not station_id:
        print("선택한 정류장의 ID가 없습니다.")
        return

    try:
        arrivals = get_bus_arrival(station_id)
    except RuntimeError as error:
        print(error)
        return

    if not arrivals:
        print("도착 정보가 없습니다.")
        return

    for item in arrivals:
        route = item.get("route", "-")
        time1 = item.get("time1", "-")
        time2 = item.get("time2", "-")
        print(f"{route}번 버스 → {time1}분 / {time2}분")


if __name__ == "__main__":
    main()
