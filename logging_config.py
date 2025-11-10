"""
Centralized logging configuration for AI Stock Research Tool

Provides structured logging with different formats for dev/prod environments.
"""
import logging
import sys
from typing import Optional
from pathlib import Path


class LogConfig:
    """Logging configuration manager"""

    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    @classmethod
    def setup_logging(
        cls,
        level: str = "INFO",
        log_file: Optional[Path] = None,
        json_format: bool = False
    ) -> logging.Logger:
        """
        Set up application logging

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for logs
            json_format: Use JSON format (for production)

        Returns:
            Configured logger instance
        """
        log_level = cls.LOG_LEVELS.get(level.upper(), logging.INFO)

        # Create logger
        logger = logging.getLogger("ai_stock_research")
        logger.setLevel(log_level)

        # Remove existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if json_format:
            # JSON format for production
            formatter = logging.Formatter(
                '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s",'
                '"function":"%(funcName)s","line":%(lineno)d,"message":"%(message)s"}'
            )
        else:
            # Human-readable format for development
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return logging.getLogger(f"ai_stock_research.{name}")
