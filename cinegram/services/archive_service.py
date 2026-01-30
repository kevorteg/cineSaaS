import requests
import logging

logger = logging.getLogger(__name__)

class ArchiveService:
    BASE_URL = "https://archive.org/metadata/"

    @staticmethod
    def get_metadata(identifier: str) -> dict:
        """Fetches metadata and file list for a given identifier."""
        url = f"{ArchiveService.BASE_URL}{identifier}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching metadata for {identifier}: {e}")
            return None
