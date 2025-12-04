import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class HomeAssistantEntities:
    users: str
    movies: str
    series: str
    episodes: str
    zfs_health: str | None = None
    zfs_capacity: str | None = None


@dataclass
class ZfsConfig:
    enabled: bool
    pool: str | None


@dataclass
class AppConfig:
    jellyfin_url: str
    jellyfin_api_key: str
    home_assistant_url: str
    home_assistant_token: str
    interval_seconds: int
    entities: HomeAssistantEntities
    zfs: ZfsConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        jellyfin_url = _require_env("JELLYFIN_URL")
        jellyfin_api_key = _require_env("JELLYFIN_API_KEY")
        home_assistant_url = _require_env("HA_URL")
        home_assistant_token = _require_env("HA_TOKEN")
        interval_seconds = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))

        zfs_enabled = os.getenv("ENABLE_ZFS", "false").lower() in {"1", "true", "yes"}
        zfs_pool = os.getenv("ZFS_POOL") if zfs_enabled else None

        entities = HomeAssistantEntities(
            users=_require_env("HA_ENTITY_USERS"),
            movies=_require_env("HA_ENTITY_MOVIES"),
            series=_require_env("HA_ENTITY_SERIES"),
            episodes=_require_env("HA_ENTITY_EPISODES"),
            zfs_health=os.getenv("HA_ENTITY_ZFS_HEALTH"),
            zfs_capacity=os.getenv("HA_ENTITY_ZFS_CAPACITY"),
        )

        if zfs_enabled:
            if not zfs_pool:
                raise ValueError("ENABLE_ZFS is set but ZFS_POOL is missing")
            if not entities.zfs_health or not entities.zfs_capacity:
                raise ValueError(
                    "ENABLE_ZFS is set but HA_ENTITY_ZFS_HEALTH or HA_ENTITY_ZFS_CAPACITY is missing"
                )

        return cls(
            jellyfin_url=_normalize_url(jellyfin_url),
            jellyfin_api_key=jellyfin_api_key,
            home_assistant_url=_normalize_url(home_assistant_url),
            home_assistant_token=home_assistant_token,
            interval_seconds=interval_seconds,
            entities=entities,
            zfs=ZfsConfig(enabled=zfs_enabled, pool=zfs_pool),
        )

    def metric_map(self) -> Dict[str, str]:
        metrics = {
            "users": self.entities.users,
            "movies": self.entities.movies,
            "series": self.entities.series,
            "episodes": self.entities.episodes,
        }

        if self.zfs.enabled:
            if self.entities.zfs_health:
                metrics["zfs_health"] = self.entities.zfs_health
            if self.entities.zfs_capacity:
                metrics["zfs_capacity"] = self.entities.zfs_capacity

        return metrics


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _normalize_url(url: str) -> str:
    return url.rstrip("/")
