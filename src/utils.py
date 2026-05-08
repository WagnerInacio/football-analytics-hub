import time
from config import REQUEST_DELAY

def smart_delay():
    """Implements a delay to respect API rate limits."""
    time.sleep(REQUEST_DELAY)

def format_column_names(name: str) -> str:
    """Standardizes column names."""
    return name.strip().replace(' ', '_').lower()
