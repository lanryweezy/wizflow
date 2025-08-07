import logging
import sys

def setup_logger(verbose: bool = False):
    """
    Configures the root logger for the application.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Create a logger
    logger = logging.getLogger('wizflow')
    logger.setLevel(level)

    # Create a handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(message)s') # Simple formatter, just the message
    handler.setFormatter(formatter)

    # Add the handler to the logger
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

# Get a logger instance for any module that needs it
def get_logger(name: str):
    return logging.getLogger(f'wizflow.{name}')
