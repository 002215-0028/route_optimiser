import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from engine.assemble import assemble_itinerary
from engine.distances import travel_time_matrix
from engine.schedule import greedy_order, schedule_day

load_dotenv()
api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
if not api_key:
    sys.exit("Missing GOOGLE_MAPS_API_KEY in .env")

trip = json.loads(Path("data/clustered.json").read_text(encoding="utf-8"))
d0 = date.fromisoformat(trip["dates"]["start"])

all_ids = [trip["start_point"]["place_id"]] + [p["place_id"] for p in trip["places"]]
matrix = travel_time_matrix(all_ids, api_key, mode="walking")
index_of = {pid: i for i, pid in enumerate(all_ids)}
START = 0

num_days = (date.fromisoformat(trip["dates"]["end"]) - d0).days + 1
plan = []
for day_num in range(1, num_days + 1):
    day_date = d0 + timedelta(days=day_num - 1)
    day_places = [p for p in trip["places"] if p.get("day") == day_num]
    ordered = greedy_order(day_places, matrix, index_of, START)
    stops = schedule_day(day_date, ordered, matrix, index_of, START)
    plan.append({"day": day_num, "date": day_date.isoformat(),
                 "weekday": day_date.strftime("%A"), "stops": stops})

for day in plan:
    print(f'\nDay {day["day"]} — {day["weekday"]} {day["date"]}')
    if not day["stops"]:
        print("   (free day)")
    for s in day["stops"]:
        flags = ("  ⚠ " + "; ".join(s["warnings"])) if s["warnings"] else ""
        print(f'   walk {s["walk_min"]:>3} min → {s["arrival"]} arrive  '
              f'{s["start"]}–{s["leave"]}  {s["name"]}{flags}')

itinerary = assemble_itinerary(trip["dates"], trip["start_point"], plan)
Path("data/itinerary.json").write_text(
    json.dumps(itinerary, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nWritten to data/itinerary.json — the engine's final output.")
