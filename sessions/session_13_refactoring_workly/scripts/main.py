#!/usr/bin/env python3
"""
Workly Application Entry Point
Hybrid Unity + Python desktop avatar application.
"""

# CRITICAL: Load .env FIRST, before any imports that might use environment variables
from dotenv import load_dotenv

load_dotenv()

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.app import WorklyApp
from src.utils.logger import setup_logger


def main():
    """Main entry point for Workly application."""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Workly application...")

    try:
        # Create and run the application
        app = WorklyApp(sys.argv)
        exit_code = app.run()
        logger.info(f"Application exited with code {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
