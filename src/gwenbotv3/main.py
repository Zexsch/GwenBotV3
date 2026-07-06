import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=wrong-import-position
from gwenbotv3 import SingletonLogger
from gwenbotv3 import App

logger = SingletonLogger(debug=False).get_logger()

if __name__ == "__main__":
    logger.info("Starting app.")
    app = App()
    app.run(token=os.environ["TOKEN"])
