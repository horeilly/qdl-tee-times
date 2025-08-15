# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python service that fetches available tee times from Quinta do Lago golf courses using their booking API. The service searches for tee times across multiple dates, times, and courses, then formats the results into a pandas DataFrame.

## Development Setup

This project uses Poetry for dependency management. Key commands:

```bash
# Install dependencies
poetry install

# Format code with Black
poetry run black .

# Run the main script
poetry run python main.py
```

## Code Architecture

The codebase consists of a single main module (`main.py`) that:

1. **Configuration**: Defines search parameters (date range, time range, number of players, course IDs)
2. **API Integration**: Fetches tee time availability from `https://api.bookgolfquintadolago.com/api/v1/golf/availability/`
3. **Data Processing**: Formats API responses into structured records with course names, prices, and starting holes
4. **Output**: Generates a pandas DataFrame with columns: date, time, course, price, players, start_hole

### Key Components

- `fetch_tee_times()`: Makes API requests for specific date/time/course combinations
- `format_tee_times()`: Transforms API response into structured records
- `COURSE_NAME_MAP`: Maps course IDs to human-readable names (South Course, North Course, Laranjal)

## Dependencies

- **pandas**: Data manipulation and DataFrame creation
- **requests**: HTTP API calls to the golf booking service
- **black**: Code formatting (line length: 88 characters, Python 3.12+ target)

## Code Style

The project uses Black formatter with the following configuration:
- Line length: 88 characters
- Target Python version: 3.12+
- Preview features enabled