"""
Configuration management for the Quinta do Lago tee time service.
"""

from datetime import date

from pydantic import Field
from pydantic_settings import BaseSettings

from qdl.models import SearchParameters


class QDLConfig(BaseSettings):
    """Configuration settings for QDL service."""

    # API Configuration
    api_url: str = Field(
        default="https://api.bookgolfquintadolago.com/api/v1/golf/availability/",
        description="Quinta do Lago API URL",
    )
    api_timeout: int = Field(default=30, description="API request timeout in seconds")

    # Default Search Parameters
    start_date: str = Field(default="2025-09-24", description="Default start date")
    end_date: str = Field(default="2025-09-30", description="Default end date")
    start_hour: int = Field(default=7, description="Default start hour")
    end_hour: int = Field(default=16, description="Default end hour")
    n_players: int = Field(default=4, description="Default number of players")

    class Config:
        env_prefix = "QDL_"


# Course ID to human-readable name mapping
COURSE_NAME_MAP: dict[str, str] = {
    "Sul": "South Course",
    "Norte": "North Course",
    "Laranjal": "Laranjal",
}

# Course IDs for API requests
COURSE_IDS = [
    "35130-201-0000000001",  # South Course
    "35130-201-0000000002",  # North Course
    "35130-201-0000000003",  # Laranjal
]


def get_default_search_params() -> SearchParameters:
    """Get default search parameters."""
    config = QDLConfig()

    return SearchParameters(
        start_date=date.fromisoformat(config.start_date),
        end_date=date.fromisoformat(config.end_date),
        start_hour=config.start_hour,
        end_hour=config.end_hour,
        n_players=config.n_players,
        course_ids=COURSE_IDS,
    )


def get_config() -> QDLConfig:
    """Get application configuration."""
    return QDLConfig()
