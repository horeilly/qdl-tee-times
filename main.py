#!/usr/bin/env python3
"""
Quinta do Lago Tee Time Service

A Python service that fetches available tee times from Quinta do Lago golf courses
using their booking API.

Usage:
    python main.py [options]

Examples:
    python main.py --start-date 2025-09-24 --end-date 2025-09-30
    python main.py --players 2 --courses south north --output results.csv
    python main.py --display --verbose
"""

from qdl.cli import main

if __name__ == "__main__":
    main()
