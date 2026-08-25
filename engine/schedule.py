from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

DEFAULT_DURATION_MIN = 90
DAY_START = "09:00"


def greedy_order(day_places: List[dict], matrix: List[List[Optional[int]]],
                 index_of: Dict[str, int], start_idx: int) -> List[dict]:
    """Order one day's stops: always walk to the nearest unvisited stop."""
    remaining = list(day_places)
    ordered = []
    current = start_idx
    while remaining:
        nearest = min(
            remaining,
            key=lambda p: matrix[current][index_of[p["place_id"]]] or 10**9,
        )
        ordered.append(nearest)
        remaining.remove(nearest)
        current = index_of[nearest["place_id"]]
    return ordered


def schedule_day(day_date, ordered, matrix, index_of, start_idx, winners=None)::
    """Walk the ordered stops with a clock; wait for openings, flag problems."""
    clock = datetime.combine(day_date, datetime.strptime(DAY_START, "%H:%M").time())
    weekday = day_date.strftime("%A")
    current = start_idx
    stops = []

    for p in ordered:
        pid = index_of[p["place_id"]]
        walk_sec = matrix[current][pid] or 0
        leg_mode = (winners[current][pid] if winners else None) or "walking"
        clock += timedelta(seconds=walk_sec)
        arrival = clock
        warnings = []

        hours = p.get("hours")
        if hours and weekday in hours.get("closed_days", []):
            warnings.append(f"CLOSED on {weekday}s")

        # fixed appointment: wait for it, or flag if we're late
        appt = p.get("appointment")
        if appt and appt.get("date") == day_date.isoformat():
            appt_dt = datetime.combine(
                day_date, datetime.strptime(appt["time"], "%H:%M").time())
            if clock <= appt_dt:
                clock = appt_dt
            else:
                warnings.append(f'LATE for {appt["time"]} appointment')

        # opening hours: wait if early, flag if it closes on us
        if hours:
            open_dt = datetime.combine(
                day_date, datetime.strptime(hours["open"], "%H:%M").time())
            close_dt = datetime.combine(
                day_date, datetime.strptime(hours["close"], "%H:%M").time())
            if clock < open_dt:
                clock = open_dt
            leave = clock + timedelta(minutes=p.get("duration_min", DEFAULT_DURATION_MIN))
            if clock >= close_dt:
                warnings.append("arrives after closing")
            elif leave > close_dt:
                warnings.append("visit runs past closing — tight")
        else:
            leave = clock + timedelta(minutes=p.get("duration_min", DEFAULT_DURATION_MIN))

        stops.append({
            "name": p["name"],
            "priority": p["priority"],
            "place_id": p["place_id"],
            "lat": p["lat"],
            "lng": p["lng"],
            "walk_min": walk_sec // 60,
            "travel_mode": leg_mode,
            "arrival": arrival.strftime("%H:%M"),
            "start": clock.strftime("%H:%M"),
            "leave": leave.strftime("%H:%M"),
            "warnings": warnings,
        })
        clock = leave
        current = pid

    return stops