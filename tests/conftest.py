"""Shared test configuration."""

import sys
import logging


def pytest_configure(config):
    """Install excepthook to prevent PyQt6 SIGABRT on unhandled exceptions."""
    def _excepthook(exc_type, exc_value, exc_tb):
        logging.error("Unhandled exception in test", exc_info=(exc_type, exc_value, exc_tb))
    sys.excepthook = _excepthook
