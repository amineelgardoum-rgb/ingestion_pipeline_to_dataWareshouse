import os
import logging
from pathlib import Path

def clean_text(val):
    """Clean text by removing newlines, tabs, and collapsing multiple spaces."""
    if isinstance(val, str):
        val = val.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        val = ' '.join(val.split())
    return val

def get_project_root():
    """Returns the absolute path to the project root directory."""
    return Path(__file__).parent.parent.parent

def setup_logging(name="pipeline"):
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
