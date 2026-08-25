from typing import List


def assemble_itinerary(trip_dates: dict, start_point: dict, days: List[dict]) -> dict:
    """Shape the final itinerary: the contract the API/UI will consume."""
    out_days = []
    total_stops = 0
    total_walk_min = 0
    all_warnings = []

    for day in days:
        legs = []
        prev_name = start_point["name"]
        for s in day["stops"]:
            legs.append({
                "from": prev_name,
                "to": s["name"],
                "walk_min": s["walk_min"],
                "mode": s.get("travel_mode", "walking"),
            })
            prev_name = s["name"]

        stops = [{
            "name": s["name"],
            "priority": s["priority"],
            "place_id": s["place_id"],
            "lat": s["lat"],
            "lng": s["lng"],
            "arrival": s["arrival"],
            "visit_start": s["start"],
            "visit_end": s["leave"],
            "warnings": s["warnings"],
        } for s in day["stops"]]

        total_stops += len(stops)
        total_walk_min += sum(l["walk_min"] for l in legs)
        for s in stops:
            for w in s["warnings"]:
                all_warnings.append({"day": day["day"], "place": s["name"], "warning": w})

        out_days.append({
            "day": day["day"],
            "date": day["date"],
            "weekday": day["weekday"],
            "stops": stops,
            "legs": legs,
        })

    return {
        "version": 1,
        "trip": trip_dates,
        "start_point": {
            "name": start_point["name"],
            "lat": start_point["lat"],
            "lng": start_point["lng"],
            "place_id": start_point["place_id"],
        },
        "summary": {
            "num_days": len(out_days),
            "total_stops": total_stops,
            "total_walk_min": total_walk_min,
            "warnings": all_warnings,
        },
        "days": out_days,
    }