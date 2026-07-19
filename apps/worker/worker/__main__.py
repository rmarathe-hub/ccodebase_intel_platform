"""Background worker entrypoint.

Job claiming and indexing land in a later day. This process stays alive for Compose.
"""

from __future__ import annotations

import logging
import time


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("codeintel.worker")


def main() -> None:
    logger.info("Worker started (idle placeholder)")
    while True:
        time.sleep(30)
        logger.info("Worker heartbeat")


if __name__ == "__main__":
    main()
