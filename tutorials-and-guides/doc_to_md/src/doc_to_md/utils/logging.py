"""Enhanced logging helper with both Rich console and Python logging."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

console = Console()

# Global logger instance
_logger: Optional[logging.Logger] = None


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
) -> logging.Logger:
    """
    Configure application logging with Rich console and optional file output.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional path to log file
        enable_console: Whether to enable console output
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Create logger
    logger = logging.getLogger("doc_to_md")
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Add Rich console handler
    if enable_console:
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
        )
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter("%(message)s", datefmt="[%X]")
        )
        logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get the configured logger, creating it with defaults if needed."""
    global _logger
    if _logger is None:
        return configure_logging()
    return _logger


def log_info(message: str) -> None:
    """Log an info message."""
    logger = get_logger()
    logger.info(message)


def log_error(message: str) -> None:
    """Log an error message."""
    logger = get_logger()
    logger.error(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    logger = get_logger()
    logger.warning(message)


def log_debug(message: str) -> None:
    """Log a debug message."""
    logger = get_logger()
    logger.debug(message)
