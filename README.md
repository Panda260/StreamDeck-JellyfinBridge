# StreamDeck-JellyfinBridge

A lightweight Python bridge that pulls Jellyfin statistics and forwards them into Home Assistant helper entities. Expose those helper values to your Stream Deck using the Home Assistant plug-in to build live status indicators.

## Features

- Polls Jellyfin for current totals of users, movies, series, and episodes
- Publishes counts into dedicated Home Assistant helper entities (e.g., counters/input_numbers)
- Configurable entirely through environment variables for Docker deployments
- Adjustable polling interval to control API frequency

## Environment variables

| Name                    | Description                                                                       |
| ----------------------- | --------------------------------------------------------------------------------- |
| `JELLYFIN_URL`          | Base URL of your Jellyfin server (e.g., `http://jellyfin:8096`).                  |
| `JELLYFIN_API_KEY`      | Jellyfin API key with permission to read library and user data.                   |
| `HA_URL`                | Base URL of Home Assistant (e.g., `http://homeassistant:8123`).                   |
| `HA_TOKEN`              | Long-lived access token for Home Assistant.                                       |
| `SYNC_INTERVAL_SECONDS` | Polling interval in seconds (default: `300`).                                     |
| `HA_ENTITY_USERS`       | Entity ID of the Home Assistant helper that should store the Jellyfin user count. |
| `HA_ENTITY_MOVIES`      | Entity ID for the movie counter helper.                                           |
| `HA_ENTITY_SERIES`      | Entity ID for the series counter helper.                                          |
| `HA_ENTITY_EPISODES`    | Entity ID for the episode counter helper.                                         |

All helper entities must already exist in Home Assistant (for example as `counter` or `input_number` helpers). The bridge simply sets their `state` value.

## Running locally

Install dependencies and run the bridge directly:

```bash
pip install -r requirements.txt
python -m bridge
```

## Docker Compose example

```yaml
services:
  jellyfin-bridge:
    image: ghcr.io/panda260/streamdeck-jellyfinbridge:latest
    build: .
    environment:
      JELLYFIN_URL: "http://jellyfin:8096"
      JELLYFIN_API_KEY: "your-jellyfin-api-key"
      HA_URL: "http://homeassistant:8123"
      HA_TOKEN: "your-homeassistant-token"
      SYNC_INTERVAL_SECONDS: 300
      HA_ENTITY_USERS: "counter.jellyfin_users"
      HA_ENTITY_MOVIES: "counter.jellyfin_movies"
      HA_ENTITY_SERIES: "counter.jellyfin_series"
      HA_ENTITY_EPISODES: "counter.jellyfin_episodes"
    restart: unless-stopped
```

Point your Stream Deck Home Assistant plug-in at the helper entities to display the live values.
