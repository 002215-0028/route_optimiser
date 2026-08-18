import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from engine.cluster import kmeans
from engine.distances import travel_time_matrix

load_dotenv()

api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
if not api_key:
    sys.exit("Missing GOOGLE_MAPS_API_KEY in .env")

trip = json.loads(Path("data/geocoded.json").read_text(encoding="utf-8"))

# --- how many days? ---
d0 = date.fromisoformat(trip["dates"]["start"])
d1 = date.fromisoformat(trip["dates"]["end"])
num_days = (d1 - d0).days + 1
print(f"Trip: {d0} to {d1} = {num_days} days\n")

# --- travel-time matrix over start point + all places ---
all_ids = [trip["start_point"]["place_id"]] + [p["place_id"] for p in trip["places"]]
matrix = travel_time_matrix(all_ids, api_key, mode="walking")

names = ["START"] + [p["name"].split(",")[0] for p in trip["places"]]
print("Travel-time matrix (minutes, walking):")
print(f'{"":<22}' + "".join(f"{n[:8]:>9}" for n in names))
for i, row in enumerate(matrix):
    cells = "".join(f'{(v // 60 if v is not None else "?"):>9}' for v in row)
    print(f"{names[i][:20]:<22}{cells}")

# --- cluster places (not the start point) into days ---
coords = [(p["lat"], p["lng"]) for p in trip["places"]]
labels = kmeans(coords, num_days)

print("\nProposed day clusters (geography only, unordered):")
for day in range(num_days):
    members = [p for p, lab in zip(trip["places"], labels) if lab == day]
    if not members:
        print(f"  Day {day + 1}: (empty)")
        continue
    print(f"  Day {day + 1}:")
    for p in members:
        print(f'    [{p["priority"]:>8}] {p["name"]}')

# --- save for Step 4 ---
for p, lab in zip(trip["places"], labels):
    p["day"] = lab + 1
out = Path("data/clustered.json")
out.write_text(json.dumps(trip, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nWritten to {out} — this feeds Step 4.")