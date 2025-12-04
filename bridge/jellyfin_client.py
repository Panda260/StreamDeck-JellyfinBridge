from __future__ import annotations

import logging
from typing import Dict

import requests

logger = logging.getLogger(__name__)


class JellyfinClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({"X-Emby-Token": api_key})

    def get_counts(self) -> Dict[str, int]:
        counts = self._get_library_counts()
        counts["users"] = self._get_user_count()
        return counts

    def _get_library_counts(self) -> Dict[str, int]:
        url = f"{self.base_url}/Items/Counts"
        logger.debug("Requesting Jellyfin library counts from %s", url)
        response = self._session.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        return {
            "movies": int(payload.get("MovieCount", 0)),
            "series": int(payload.get("SeriesCount", 0)),
            "episodes": int(payload.get("EpisodeCount", 0)),
        }

    def _get_user_count(self) -> int:
        url = f"{self.base_url}/Users"
        logger.debug("Requesting Jellyfin users from %s", url)
        response = self._session.get(url, timeout=10)
        response.raise_for_status()
        users = response.json()
        if isinstance(users, list):
            return len(users)
        return int(users.get("TotalRecordCount", 0))
