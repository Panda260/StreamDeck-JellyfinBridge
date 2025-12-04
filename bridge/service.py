import logging
import time

from .config import AppConfig
from .home_assistant_client import HomeAssistantClient
from .jellyfin_client import JellyfinClient
from .zfs_client import ZfsClient

logger = logging.getLogger(__name__)


class BridgeService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.jellyfin = JellyfinClient(config.jellyfin_url, config.jellyfin_api_key)
        self.home_assistant = HomeAssistantClient(
            config.home_assistant_url, config.home_assistant_token
        )
        self.zfs = ZfsClient(config.zfs.pool) if config.zfs.enabled and config.zfs.pool else None

    def run_forever(self) -> None:
        logger.info("Starting Jellyfin -> Home Assistant bridge with %s second interval", self.config.interval_seconds)
        while True:
            try:
                self.run_once()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error during sync: %s", exc)
            time.sleep(self.config.interval_seconds)

    def run_once(self) -> None:
        counts = self.jellyfin.get_counts()
        if self.zfs:
            try:
                zfs_metrics = self.zfs.get_metrics()
                counts.update(zfs_metrics)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error while collecting ZFS metrics: %s", exc)
        metric_map = self.config.metric_map()

        for metric, entity_id in metric_map.items():
            value = counts.get(metric, 0)
            logger.info("Sending %s=%s to Home Assistant entity %s", metric, value, entity_id)
            self.home_assistant.update_state(entity_id, value)


__all__ = ["BridgeService"]
