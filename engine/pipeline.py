from datetime import date, timedelta
from typing import Optional

from engine.geocode import geocode
from engine.distances import travel_time_matrix
from engine.cluster import kmeans
from engine.schedule import greedy_order, schedule_day
from engine.assemble import assemble_itinerary


def plan_trip(trip: dict, api_key: str, mode: str = "walking") -> dict:
    """Run the full pipeline: geocode -> distances -> cluster -> order -> schedule.

    `trip` matches the trip.json shape. Returns the versioned itinerary dict.
    """
    region: Optional[str] = trip.get("region")

    # 1. geocode everything
    start = dict(trip["start_point"])
    start.update(geocode(start["name"], api_key, region))
    places = []
    for p in trip["places"]:
        place = dict(p)
        place.update(geocode(place["name"], api_key, region))
        places.append(place)

    # 2. travel-time matrix
    all_ids = [start["place_id"]] + [p["place_id"] for p in places]
    matrix = travel_time_matrix(all_ids, api_key, mode=mode)
    index_of = {pid: i for i, pid in enumerate(all_ids)}

    # 3. cluster into days
    d0 = date.fromisoformat(trip["dates"]["start"])
    d1 = date.fromisoformat(trip["dates"]["end"])
    num_days = (d1 - d0).days + 1
    labels = kmeans([(p["lat"], p["lng"]) for p in places], num_days)
    for p, lab in zip(places, labels):
        p["day"] = lab + 1

    # 4. order + schedule each day
    plan = []
    for day_num in range(1, num_days + 1):
        day_date = d0 + timedelta(days=day_num - 1)
        day_places = [p for p in places if p["day"] == day_num]
        ordered = greedy_order(day_places, matrix, index_of, 0)
        stops = schedule_day(day_date, ordered, matrix, index_of, 0)
        plan.append({
            "day": day_num,
            "date": day_date.isoformat(),
            "weekday": day_date.strftime("%A"),
            "stops": stops,
        })

    # 5. assemble the contract
    return assemble_itinerary(trip["dates"], start, plan)