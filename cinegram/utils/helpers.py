import re

def is_valid_archive_url(url: str) -> bool:
    """Checks if the URL is a valid Internet Archive identifier."""
    return "archive.org/details/" in url

def extract_identifier(url: str) -> str:
    """Extracts the identifier from an Internet Archive URL."""
    # Pattern to match: ...archive.org/details/IDENTIFIER
    match = re.search(r"archive\.org/details/([^/]+)", url)
    if match:
        return match.group(1)
    return None
