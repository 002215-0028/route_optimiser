import requests
from typing import Optional
from engine.cache import load_cache, save_cache

BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def geocode(name: str, api_key: str, region: Optional[str] = None) -> dict:
    """Resolve a place name to coordinates + place_id via the Geocoding API.

    Returns: {"lat": float, "lng": float, "formatted_address": str, "place_id": str}
    Raises: RuntimeError if the name cannot be resolved.
    """
    cache = load_cache("geocode")
    cache_key = f"{region}::{name}" if region else name
    if cache_key in cache:
        return cache[cache_key]

    params = {"address": name, "key": api_key}
    if region:
        params["region"] = region

    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data["status"] != "OK" or not data.get("results"):
        raise RuntimeError(
            f'Geocoding failed for "{name}": {data["status"]} '
            f'{data.get("error_message", "")}'
        )

    top = data["results"][0]
    result = {
        "lat": top["geometry"]["location"]["lat"],
        "lng": top["geometry"]["location"]["lng"],
        "formatted_address": top["formatted_address"],
        "place_id": top["place_id"],
    }

    cache[cache_key] = result
    save_cache("geocode", cache)
    return result