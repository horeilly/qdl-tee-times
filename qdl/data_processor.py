"""
Data processing utilities for tee time data.
"""

import logging
import pandas as pd

from qdl.models import CourseAvailabilityResponse, TeeTimeRecord
from qdl.config import COURSE_NAME_MAP

logger = logging.getLogger(__name__)


class TeeTimeProcessor:
    """Processes tee time data from API responses."""

    @staticmethod
    def format_tee_times(
        response: CourseAvailabilityResponse, search_date: str
    ) -> list[TeeTimeRecord]:
        """
        Convert API response to formatted tee time records.

        Args:
            response: CourseAvailabilityResponse from API
            search_date: Date in YYYY-MM-DD format

        Returns:
            List of TeeTimeRecord objects
        """
        course_name = COURSE_NAME_MAP.get(response.name, response.name)
        records = []

        for availability in response.availabilities:
            # Convert start_nine to starting hole number
            start_hole = 1 if availability.start_nine == 1 else 10

            record = TeeTimeRecord(
                date=search_date,
                time=availability.time,
                course=course_name,
                price=availability.price,
                players=availability.players,
                start_hole=start_hole,
            )
            records.append(record)

        logger.debug(
            f"Formatted {len(records)} tee times for {course_name} on {search_date}"
        )
        return records

    @staticmethod
    def records_to_dataframe(records: list[TeeTimeRecord]) -> pd.DataFrame:
        """
        Convert tee time records to pandas DataFrame.

        Args:
            records: List of TeeTimeRecord objects

        Returns:
            pandas DataFrame with tee time data
        """
        if not records:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(
                columns=["date", "time", "course", "price", "players", "start_hole"]
            )

        # Convert records to list of dictionaries
        data = [record.model_dump() for record in records]
        df = pd.DataFrame(data)

        # Remove duplicates and sort
        df = df.drop_duplicates().sort_values(["date", "time", "course"])
        df = df.reset_index(drop=True)

        logger.info(f"Created DataFrame with {len(df)} unique tee time records")
        return df

    @staticmethod
    def save_dataframe(df: pd.DataFrame, filename: str) -> None:
        """
        Save DataFrame to various formats based on file extension.

        Args:
            df: pandas DataFrame to save
            filename: Output filename with extension (.csv, .xlsx, .json)
        """
        if filename.endswith(".csv"):
            df.to_csv(filename, index=False)
        elif filename.endswith(".xlsx"):
            df.to_excel(filename, index=False)
        elif filename.endswith(".json"):
            df.to_json(filename, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

        logger.info(f"Saved {len(df)} records to {filename}")
