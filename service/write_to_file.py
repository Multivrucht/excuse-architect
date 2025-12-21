""" To be replaced with proper DB.. temp solution. """

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def write_to_file(data: str | None):
    """
    Append data to file, to be replaced with proper DB, not text file
    """

    if not data:
        logger.error("Writing empty data to DB..")
        raise ValueError("Cannot write empty data")
    
    filepath = Path('storage/stored_API_responses.txt')
    filepath.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    
    with filepath.open(mode="a", encoding="utf-8") as f:
        chars_written = f.write(data + "\n")
    
    logger.info(f"Written {chars_written} to {filepath}")