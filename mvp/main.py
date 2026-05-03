from bus import get_bus_arrival
from station import find_station


def main():
    keyword = input("정류장 이름을 입력하세요: ").strip()
    stations = find_station(keyword)

    if not stations:
        print("정류장을 찾을 수 없습니다.")
        return

    for i, station in enumerate(stations, start=1):
        print(f"{i}. {station.get('STATION_NM', '')}")

    choice = input("번호를 선택하세요: ").strip()
    if not choice.isdigit():
        print("잘못된 선택입니다.")
        return

    index = int(choice) - 1
    if index < 0 or index >= len(stations):
        print("잘못된 선택입니다.")
        return

    station_id = stations[index].get("STATION_ID")
    try:
        arrivals = get_bus_arrival(station_id)
    except RuntimeError as e:
        print(e)
        return

    if not arrivals:
        print("도착 정보가 없습니다.")
        return

    for bus in arrivals:
        print(f"{bus['route']}번 버스 → {bus['time1']}분 / {bus['time2']}분")


if __name__ == "__main__":
    main()
