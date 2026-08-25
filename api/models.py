from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from typing_extensions import Literal


class Hours(BaseModel):
    open: str = Field(pattern=r"^\d{2}:\d{2}$")
    close: str = Field(pattern=r"^\d{2}:\d{2}$")
    closed_days: List[str] = []


class Appointment(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")


class PlaceIn(BaseModel):
    name: str = Field(min_length=1)
    priority: Literal["must", "want", "optional"]
    hours: Optional[Hours] = None
    duration_min: Optional[int] = Field(default=None, ge=15, le=600)
    appointment: Optional[Appointment] = None


class Dates(BaseModel):
    start: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    end: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class StartPoint(BaseModel):
    name: str = Field(min_length=1)


from pydantic import BaseModel, Field, field_validator

class TripIn(BaseModel):
    dates: Dates
    region: Optional[str] = None
    start_point: StartPoint
    places: List[PlaceIn] = Field(min_length=1, max_length=25)
    modes: List[Literal["walking", "transit", "driving", "bicycling"]] = ["walking"]

    @field_validator("modes")
    @classmethod
    def at_least_one_mode(cls, v):
        if not v:
            raise ValueError("at least one travel mode required")
        return list(dict.fromkeys(v))  # dedupe, keep order