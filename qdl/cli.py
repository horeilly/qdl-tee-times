"""
Command-line interface for the Quinta do Lago tee time service.
"""

import argparse
import logging
import sys
from datetime import date

import pandas as pd

from qdl.api_client import QDLAPIClient, QDLAPIError
from qdl.config import get_default_search_params, get_config, COURSE_IDS
from qdl.data_processor import TeeTimeProcessor
from qdl.models import SearchParameters


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Fetch available tee times from Quinta do Lago golf courses"
    )

    # Date range
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")

    # Time range
    parser.add_argument(
        "--start-hour", type=int, choices=range(0, 24), help="Start hour (0-23)"
    )
    parser.add_argument(
        "--end-hour", type=int, choices=range(0, 24), help="End hour (0-23)"
    )

    # Players
    parser.add_argument(
        "--players", type=int, choices=range(1, 5), help="Number of players (1-4)"
    )

    # Output options
    parser.add_argument(
        "--output", type=str, help="Output file (supports .csv, .xlsx, .json)"
    )
    parser.add_argument(
        "--display", action="store_true", help="Display results in console"
    )

    # Courses
    parser.add_argument(
        "--courses",
        nargs="+",
        choices=["south", "north", "laranjal", "all"],
        default=["all"],
        help="Courses to search (default: all)",
    )

    # Other options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser


def parse_course_selection(course_args: list[str]) -> list[str]:
    """Parse course selection arguments into course IDs."""
    if "all" in course_args:
        return COURSE_IDS

    course_map = {
        "south": "35130-201-0000000001",
        "north": "35130-201-0000000002",
        "laranjal": "35130-201-0000000003",
    }

    return [course_map[course] for course in course_args if course in course_map]


def validate_date_range(start_date: date, end_date: date) -> None:
    """Validate date range."""
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")

    if start_date < date.today():
        raise ValueError("Start date cannot be in the past")


def fetch_all_tee_times(client: QDLAPIClient, params: SearchParameters) -> pd.DataFrame:
    """
    Fetch all tee times for the given parameters.

    Args:
        client: QDL API client
        params: Search parameters

    Returns:
        pandas DataFrame with all tee time results
    """
    processor = TeeTimeProcessor()
    all_records = []

    # Generate date range
    date_range = (
        pd.date_range(params.start_date, params.end_date).strftime("%Y-%m-%d").tolist()
    )

    # Generate time range
    times = [f"{hour:02d}:00" for hour in range(params.start_hour, params.end_hour + 1)]

    total_requests = len(date_range) * len(times) * len(params.course_ids)
    completed_requests = 0

    print(f"Searching {total_requests} time slots...")

    for search_date in date_range:
        print(f"Fetching tee times for {search_date}...")

        for time_slot in times:
            for course_id in params.course_ids:
                try:
                    response = client.fetch_tee_times(
                        search_date, time_slot, course_id, params.n_players
                    )
                    records = processor.format_tee_times(response, search_date)
                    all_records.extend(records)

                except QDLAPIError as e:
                    logging.warning(f"Failed to fetch {search_date} {time_slot}: {e}")

                completed_requests += 1
                if completed_requests % 10 == 0:
                    print(f"Progress: {completed_requests}/{total_requests}")

    return processor.records_to_dataframe(all_records)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        # Get default parameters and override with CLI args
        params = get_default_search_params()

        if args.start_date:
            params.start_date = date.fromisoformat(args.start_date)
        if args.end_date:
            params.end_date = date.fromisoformat(args.end_date)
        if args.start_hour is not None:
            params.start_hour = args.start_hour
        if args.end_hour is not None:
            params.end_hour = args.end_hour
        if args.players:
            params.n_players = args.players

        params.course_ids = parse_course_selection(args.courses)

        # Validate parameters
        validate_date_range(params.start_date, params.end_date)

        # Fetch tee times
        config = get_config()
        with QDLAPIClient(config) as client:
            df = fetch_all_tee_times(client, params)

        print(f"\nFound {len(df)} available tee times")

        # Output results
        if args.output:
            processor = TeeTimeProcessor()
            processor.save_dataframe(df, args.output)
            print(f"Saved results to {args.output}")

        if args.display or not args.output:
            if not df.empty:
                print("\nAvailable tee times:")
                print(df.to_string(index=False))
            else:
                print("No tee times found for the specified criteria.")

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
