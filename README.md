# StreamDeck-JellyfinBridge

A lightweight Python bridge that pulls Jellyfin statistics and forwards them into Home Assistant helper entities. Expose those helper values to your Stream Deck using the Home Assistant plug-in to build live status indicators.

## Features

- Polls Jellyfin for current totals of users, movies, series, and episodes
- Publishes counts into dedicated Home Assistant helper entities (e.g., counters/input_numbers)
- Optional ZFS pool health and capacity reporting with three-decimal precision
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
| `ENABLE_ZFS`            | Set to `true`/`1` to enable ZFS metrics collection.                               |
| `ZFS_POOL`              | Name of the ZFS pool to query (required when `ENABLE_ZFS` is enabled).            |
| `HA_ENTITY_ZFS_HEALTH`  | Entity ID that should store the ZFS pool health string (e.g., `ONLINE`).          |
| `HA_ENTITY_ZFS_CAPACITY`| Entity ID that should store the ZFS pool capacity percentage (three decimals).    |

All helper entities must already exist in Home Assistant (for example as `counter` or `input_number` helpers). The bridge simply sets their `state` value.

ZFS metrics are optional. When `ENABLE_ZFS` is `true`, the container must be able to run `zpool list` for the specified pool (e.g., by mounting your host's `zpool` directory and `/dev/zfs` read-only or by providing a ZFS exporter endpoint inside the container). Pool capacity is reported with three decimal places. The path to the `zpool` binary varies by distro—use `command -v zpool` on the host to see the exact path:

```bash
command -v zpool
# Example output: /sbin/zpool

# If nothing is printed, install ZFS tools or ensure they are in PATH.
```

Once you know the path, mount the entire directory that contains `zpool` to avoid Docker trying to create a file on a read-only root filesystem (e.g., `/sbin:/sbin:ro` or `/usr/sbin:/usr/sbin:ro`, depending on the output of the command above).

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
      # Optional ZFS metrics
      ENABLE_ZFS: "true"
      ZFS_POOL: "tank"
      HA_ENTITY_ZFS_HEALTH: "input_text.zfs_pool_health"
      HA_ENTITY_ZFS_CAPACITY: "input_number.zfs_pool_capacity"
      volumes:
        # Provide the zpool binary directory and device read-only so the container can query the pool
        # Detect the host path with: command -v zpool (commonly /sbin/zpool or /usr/sbin/zpool)
        # Mount the containing directory, not a single file, to avoid read-only filesystem errors if the path is wrong.
        - /sbin:/sbin:ro     # replace /sbin with $(dirname $(command -v zpool)) from your host
        - /dev/zfs:/dev/zfs:ro
    restart: unless-stopped
```

Point your Stream Deck Home Assistant plug-in at the helper entities to display the live values.
