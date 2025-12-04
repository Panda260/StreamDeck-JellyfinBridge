import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class HomeAssistantEntities:
    users: str
    movies: str
    series: str
    episodes: str


@dataclass
class AppConfig:
    jellyfin_url: str
    jellyfin_api_key: str
    home_assistant_url: str
    home_assistant_token: str
    interval_seconds: int
    entities: HomeAssistantEntities

    @classmethod
    def from_env(cls) -> "AppConfig":
        jellyfin_url = _require_env("JELLYFIN_URL")
        jellyfin_api_key = _require_env("JELLYFIN_API_KEY")
        home_assistant_url = _require_env("HA_URL")
        home_assistant_token = _require_env("HA_TOKEN")
        interval_seconds = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))

        entities = HomeAssistantEntities(
            users=_require_env("HA_ENTITY_USERS"),
            movies=_require_env("HA_ENTITY_MOVIES"),
            series=_require_env("HA_ENTITY_SERIES"),
            episodes=_require_env("HA_ENTITY_EPISODES"),
        )

        return cls(
            jellyfin_url=_normalize_url(jellyfin_url),
            jellyfin_api_key=jellyfin_api_key,
            home_assistant_url=_normalize_url(home_assistant_url),
            home_assistant_token=home_assistant_token,
            interval_seconds=interval_seconds,
            entities=entities,
        )

    def metric_map(self) -> Dict[str, str]:
        return {
            "users": self.entities.users,
            "movies": self.entities.movies,
            "series": self.entities.series,
            "episodes": self.entities.episodes,
        }


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _normalize_url(url: str) -> str:
    return url.rstrip("/")
