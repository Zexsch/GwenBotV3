import os

from gwenbotv3 import SingletonLogger
from gwenbotv3 import App

logger = SingletonLogger(debug=False).get_logger()

if __name__ == "__main__":
    logger.info("Starting app.")
    app = App()
    app.run(token=os.environ["TOKEN"])
