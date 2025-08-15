"""
Data models for the Quinta do Lago tee time service.
"""

from datetime import date

from pydantic import BaseModel, Field


class TeeTimeAvailability(BaseModel):
    """Represents a single tee time availability slot."""

    time: str = Field(..., description="Tee time in HH:MM format")
    price: float = Field(..., description="Price for the tee time")
    players: int = Field(..., description="Number of players for this slot")
    start_nine: int = Field(
        ..., description="Starting nine (1 for front nine, 2 for back nine)"
    )


class CourseAvailabilityResponse(BaseModel):
    """API response for course availability."""

    name: str = Field(..., description="Course name (Sul, Norte, Laranjal)")
    availabilities: list[TeeTimeAvailability] = Field(
        default_factory=list, description="List of available tee times"
    )


class TeeTimeRecord(BaseModel):
    """Formatted tee time record for output."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")
    course: str = Field(..., description="Human-readable course name")
    price: float = Field(..., description="Price for the tee time")
    players: int = Field(..., description="Number of players")
    start_hole: int = Field(..., description="Starting hole number (1 or 10)")


class SearchParameters(BaseModel):
    """Parameters for tee time search."""

    start_date: date = Field(..., description="Start date for search")
    end_date: date = Field(..., description="End date for search")
    start_hour: int = Field(7, ge=0, le=23, description="Start hour for search")
    end_hour: int = Field(16, ge=0, le=23, description="End hour for search")
    n_players: int = Field(4, ge=1, le=4, description="Number of players")
    course_ids: list[str] = Field(
        default_factory=lambda: [
            "35130-201-0000000001",
            "35130-201-0000000002",
            "35130-201-0000000003",
        ],
        description="List of course IDs to search",
    )
