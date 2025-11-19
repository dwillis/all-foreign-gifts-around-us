"""
Logging utility for Foreign Gifts Tracker.
Provides structured logging with file and console output.
"""

import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional


def setup_logging(
    config_path: Optional[str] = None,
    default_level: int = logging.INFO
) -> None:
    """
    Setup logging configuration.

    Args:
        config_path: Path to logging config YAML file
        default_level: Default logging level if config not found
    """
    # Try to load logging config
    if config_path is None:
        config_path = "config/logging.yaml"

    path = Path(config_path)

    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    if path.exists():
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        # Fallback to basic configuration
        logging.basicConfig(
            level=default_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/gifts_tracker.log'),
                logging.StreamHandler()
            ]
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)
