import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=wrong-import-position
from gwenbotv3.loggers import init_logging

log_dir = Path("/home/container/Logs")

init_logging(log_dir)

from gwenbotv3 import App


def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting app.")
    app = App()
    app.run(token=os.environ["TOKEN"])


if __name__ == "__main__":
    main()
