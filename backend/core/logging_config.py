"""
Logging configuration for production-grade logging.

Provides structured JSON logging with rotating file handlers,
separate log files for application and conversations.
"""

import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from pythonjsonlogger import jsonlogger


# Log directory setup
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file paths
APP_LOG_FILE = LOG_DIR / "app.log"
CONVERSATION_LOG_FILE = LOG_DIR / "conversations.log"

# Log format for console (human-readable)
CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# Maximum log file size (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024

# Number of backup files to keep
BACKUP_COUNT = 5


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Add log level
        log_record["level"] = record.levelname
        
        # Add logger name
        log_record["logger"] = record.name
        
        # Add source location
        log_record["source"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }


def get_console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    """Create a console handler with colored output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    return handler


def get_file_handler(
    log_file: Path,
    level: int = logging.INFO,
    use_json: bool = True,
) -> RotatingFileHandler:
    """Create a rotating file handler."""
    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    
    if use_json:
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(CONSOLE_FORMAT)
    
    handler.setFormatter(formatter)
    return handler


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up application-wide logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    root_logger.addHandler(get_console_handler(level))
    
    # Add file handler for app logs
    root_logger.addHandler(get_file_handler(APP_LOG_FILE, level))
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def get_conversation_logger() -> logging.Logger:
    """
    Get a dedicated logger for conversation logging.
    
    Returns:
        Logger configured to write to conversations.log
    """
    logger = logging.getLogger("conversations")
    
    # Only add handler if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(get_file_handler(CONVERSATION_LOG_FILE, logging.INFO))
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger
