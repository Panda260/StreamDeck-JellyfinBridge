import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def update_state(self, entity_id: str, value: Any) -> None:
        url = f"{self.base_url}/api/states/{entity_id}"
        logger.debug("Updating Home Assistant entity %s", entity_id)
        response = self._session.post(url, json={"state": value}, timeout=10)
        response.raise_for_status()
