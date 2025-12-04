import logging
import sys

from .config import AppConfig
from .service import BridgeService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def main() -> int:
    try:
        config = AppConfig.from_env()
    except Exception:
        logging.exception("Failed to load configuration from environment")
        return 1

    service = BridgeService(config)
    service.run_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
