"""
API client for interacting with the Quinta do Lago booking API.
"""

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import ValidationError

from qdl.models import CourseAvailabilityResponse
from qdl.config import QDLConfig

logger = logging.getLogger(__name__)


class QDLAPIError(Exception):
    """Custom exception for QDL API errors."""

    pass


class QDLAPIClient:
    """Client for interacting with the Quinta do Lago booking API."""

    def __init__(self, config: QDLConfig | None) -> None:
        """Initialize the API client."""
        self.config = config or QDLConfig()
        self.session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def fetch_tee_times(
        self, date: str, time: str, course_id: str, n_players: int
    ) -> CourseAvailabilityResponse:
        """
        Fetch tee time availability for a specific date, time, and course.

        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            course_id: Course identifier
            n_players: Number of players

        Returns:
            CourseAvailabilityResponse object with availability data

        Raises:
            QDLAPIError: If API request fails or returns invalid data
        """
        params: dict[str, str | int] = {
            "date": date,
            "time": time,
            "players": n_players,
            "course": course_id,
        }

        try:
            logger.debug(f"Fetching tee times for {date} {time} course {course_id}")

            response = self.session.get(
                self.config.api_url, params=params, timeout=self.config.api_timeout
            )
            response.raise_for_status()

            # Parse and validate response
            data = response.json()
            return CourseAvailabilityResponse.model_validate(data)

        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed for {date} {time} {course_id}: {e}"
            logger.error(error_msg)
            raise QDLAPIError(error_msg) from e

        except ValidationError as e:
            error_msg = f"Invalid API response for {date} {time} {course_id}: {e}"
            logger.error(error_msg)
            raise QDLAPIError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error for {date} {time} {course_id}: {e}"
            logger.error(error_msg)
            raise QDLAPIError(error_msg) from e

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "QDLAPIClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
