import pandas as pd
import requests

START_DATE = "2025-09-24"
END_DATE = "2025-09-30"
START_HOUR = 7
END_HOUR = 16
N_PLAYERS = 4
URL = "https://api.bookgolfquintadolago.com/api/v1/golf/availability/"

COURSE_NAME_MAP = {
    "Sul": "South Course",
    "Norte": "North Course",
    "Laranjal": "Laranjal",
}

dates = pd.date_range(START_DATE, END_DATE).strftime("%Y-%m-%d").to_list()
times = [f"{hour:02d}:00" for hour in range(START_HOUR, END_HOUR + 1)]
courses = ["35130-201-0000000001", "35130-201-0000000002", "35130-201-0000000003"]

# params = {
#     "date": "2025-09-26",
#     "time": "12:00",
#     "players": N_PLAYERS,
#     "course": "35130-201-0000000002"
# }


def fetch_tee_times(date: str, time: str, course: str) -> dict:
    params = {"date": date, "time": time, "players": N_PLAYERS, "course": course}
    response = requests.get(URL, params=params)
    return response.json()


def format_tee_times(data: dict, date: str) -> list:
    course = COURSE_NAME_MAP[data["name"]]
    tee_times = []
    for tee_time in data["availabilities"]:
        time = tee_time["time"]
        price = tee_time["price"]
        players = tee_time["players"]
        if tee_time["start_nine"] == 1:
            start_hole = 1
        elif tee_time["start_nine"] == 2:
            start_hole = 10
        else:
            start_hole = 1
        insert_record = [date, time, course, price, players, start_hole]
        tee_times.append(insert_record)
    return tee_times


results = []
for d in dates:
    print(f"Fetching tee times for {d}...")
    for t in times:
        for c in courses:
            tee_times = fetch_tee_times(d, t, c)
            formatted_tee_times = format_tee_times(tee_times, d)
            results.extend(formatted_tee_times)
df = pd.DataFrame(
    results, columns=["date", "time", "course", "price", "players", "start_hole"]
)
df.drop_duplicates()
