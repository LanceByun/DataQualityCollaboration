from bus import BusAPIError, get_bus_arrival
from station import find_station


def main():
    keyword = input("정류장 이름을 입력하세요: ").strip()
    matches = find_station(keyword)

    if not matches:
        print("검색 결과가 없습니다.")
        return

    for i, station in enumerate(matches, start=1):
        print(f"{i}. {station.get('STATION_NM', '이름없음')}")

    choice = input("정류장을 선택하세요 (번호): ").strip()
    if not choice.isdigit():
        print("잘못된 선택입니다.")
        return

    idx = int(choice) - 1
    if idx < 0 or idx >= len(matches):
        print("잘못된 선택입니다.")
        return

    station_id = matches[idx].get("STATION_ID")
    if not station_id:
        print("선택한 정류장의 STATION_ID가 없습니다.")
        return

    try:
        arrivals = get_bus_arrival(station_id)
    except BusAPIError as e:
        print(str(e))
        return

    if not arrivals:
        print("도착 정보가 없습니다.")
        return

    for row in arrivals:
        route = row.get("route", "-")
        time1 = row.get("time1", "-")
        time2 = row.get("time2", "-")
        print(f"{route}번 버스 → {time1}분 / {time2}분")


if __name__ == "__main__":
    main()
