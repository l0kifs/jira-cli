import sys

from loguru import logger

from .settings import settings




def setup_logging():
    """
    Configure logging for the application.
    """

    # Remove default handler to avoid duplicate logs
    logger.remove()

    # Console handler - for development/debugging
    logger.add(
        sys.stderr,
        level=settings.logging.level,
        format=settings.logging.console_format,
        colorize=True,  # Enable colors in console
        backtrace=True,  # Show full traceback on errors
        diagnose=True,  # Show variable values in tracebacks (disable in production for security)
        enqueue=True,  # Thread-safe logging
        catch=True,  # Catch and log logging errors
    )

    # File handler - structured JSON logging
    logger.add(
        settings.log_file_path,
        level=settings.logging.file_level,
        serialize=True,  # JSON serialization
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="gz",  # Compress rotated files
        encoding="utf-8",
        enqueue=True,
        catch=True,
    )

    # Bind common context (can be overridden per module)
    logger.bind(app=settings.app.name, version=settings.app.version)

    # Log startup message
    logger.info(
        "Logging system initialized",
        log_file=str(settings.log_file_path),
        log_level=settings.logging.level,
    )
