#!/usr/bin/env python3
"""
Desktop-Mate Application Entry Point
Hybrid Unity + Python desktop avatar application.
"""

import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.app import DesktopMateApp
from src.utils.logger import setup_logger


def main():
    """Main entry point for Desktop-Mate application."""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Desktop-Mate application...")
    
    try:
        # Create and run the application
        app = DesktopMateApp(sys.argv)
        exit_code = app.run()
        logger.info(f"Application exited with code {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
