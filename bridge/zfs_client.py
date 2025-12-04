import logging
import subprocess

logger = logging.getLogger(__name__)


class ZfsClient:
    def __init__(self, pool: str) -> None:
        self.pool = pool

    def get_metrics(self) -> dict[str, object]:
        capacity, health = self._get_pool_status()
        return {
            "zfs_capacity": f"{capacity:.3f}",
            "zfs_health": health,
        }

    def _get_pool_status(self) -> tuple[float, str]:
        command = ["zpool", "list", "-Hp", "-o", "capacity,health", self.pool]
        logger.debug("Running ZFS command: %s", " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if not output:
            raise RuntimeError("Empty output from zpool list")

        first_line = output.splitlines()[0]
        parts = first_line.split()
        if len(parts) < 2:
            raise RuntimeError(f"Unexpected zpool output: {first_line}")

        capacity_raw, health = parts[0], parts[1]
        try:
            capacity_value = float(capacity_raw)
        except ValueError as exc:  # noqa: BLE001
            raise RuntimeError(f"Unable to parse capacity value: {capacity_raw}") from exc

        return round(capacity_value, 3), health


__all__ = ["ZfsClient"]
