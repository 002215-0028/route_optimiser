import requests
from typing import List, Optional

from engine.cache import load_cache, save_cache

BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def travel_time_matrix(
    place_ids: List[str], api_key: str, mode: str = "walking"
) -> List[List[Optional[int]]]:
    """Fetch an NxN matrix of travel times (seconds) between places.

    matrix[i][j] = seconds to travel from place i to place j.
    None where Google couldn't compute a route.
    """
    cache = load_cache("distance_matrix")
    cache_key = mode + "::" + "|".join(place_ids)
    if cache_key in cache:
        return cache[cache_key]

    locs = "|".join("place_id:" + pid for pid in place_ids)
    params = {
        "origins": locs,
        "destinations": locs,
        "mode": mode,
        "key": api_key,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if data["status"] != "OK":
        raise RuntimeError(
            f'Distance Matrix failed: {data["status"]} {data.get("error_message", "")}'
        )

    matrix: List[List[Optional[int]]] = []
    for row in data["rows"]:
        matrix.append([
            el["duration"]["value"] if el["status"] == "OK" else None
            for el in row["elements"]
        ])

    cache[cache_key] = matrix
    save_cache("distance_matrix", cache)
    return matrix