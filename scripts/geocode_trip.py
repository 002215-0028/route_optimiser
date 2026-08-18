import json
import os
import sys
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from engine.geocode import geocode

load_dotenv()

api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
if not api_key:
    sys.exit("Missing GOOGLE_MAPS_API_KEY in .env")

trip = json.loads(Path("data/trip.json").read_text(encoding="utf-8"))
region: Optional[str] = None

print(f'Geocoding start point + {len(trip["places"])} places...\n')

start = geocode(trip["start_point"]["name"], api_key, region)
trip["start_point"].update(start)

for place in trip["places"]:
    place.update(geocode(place["name"], api_key, region))

# --- print a verification table ---
header = f'{"PRIORITY":<10} {"NAME":<38} {"LAT":>9} {"LNG":>9}  RESOLVED AS'
print(header)
print("-" * len(header))
print(f'{"-":<10} {"START: " + trip["start_point"]["name"]:<38.38} '
      f'{trip["start_point"]["lat"]:>9.4f} {trip["start_point"]["lng"]:>9.4f}  '
      f'{trip["start_point"]["formatted_address"]}')
for p in trip["places"]:
    print(f'{p["priority"]:<10} {p["name"]:<38.38} '
          f'{p["lat"]:>9.4f} {p["lng"]:>9.4f}  {p["formatted_address"]}')

out = Path("data/geocoded.json")
out.write_text(json.dumps(trip, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nWritten to {out} — this feeds Step 3.")