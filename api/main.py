import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.models import TripIn
from engine.pipeline import plan_trip

load_dotenv()

app = FastAPI(title="Route Optimiser API", version="1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/optimise")
def optimise(trip: TripIn) -> dict:
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Server missing API key")
    try:
        return plan_trip(trip.model_dump(), api_key)
    except RuntimeError as e:
        # engine's "couldn't geocode / matrix failed" errors -> client's fault, mostly
        raise HTTPException(status_code=422, detail=str(e))