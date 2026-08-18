import json
import os
from datetime import datetime

from airflow.decorators import dag, task

DATA = "/opt/airflow/data/trip.json"
OUTPUT = "/opt/airflow/output"


@dag(
    schedule="@daily",
    start_date=datetime(2026, 8, 1),
    catchup=False,
    tags=["routing"],
)
def route_pipeline():
    """Daily routing pipeline: ingest a day's visits -> optimise -> report."""

    @task
    def ingest() -> dict:
        """Load the day's input. Stand-in for pulling from a CRM/database."""
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)

    @task
    def optimise(trip: dict) -> dict:
        """Run the actual engine - the same plan_trip the API serves."""
        from engine.pipeline import plan_trip
        return plan_trip(trip, os.environ["GOOGLE_MAPS_API_KEY"])

    @task
    def report(itinerary: dict) -> str:
        """Summarise the plan - stand-in for emailing/Slacking the team."""
        s = itinerary["summary"]
        lines = [
            f"Route plan generated {datetime.now().isoformat(timespec='seconds')}",
            f"Days: {s['num_days']}  Stops: {s['total_stops']}  "
            f"Total travel: {s['total_walk_min']} min",
            f"Warnings: {len(s['warnings'])}",
        ]
        for w in s["warnings"]:
            lines.append(f"  - Day {w['day']}, {w['place']}: {w['warning']}")
        path = f"{OUTPUT}/report_{datetime.now():%Y%m%d_%H%M%S}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return path

    report(optimise(ingest()))


route_pipeline()