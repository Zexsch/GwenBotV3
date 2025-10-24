import os

from logger import SingletonLogger

logger = SingletonLogger(debug=False).get_logger()

from Bot.app import App

if __name__ == '__main__':
    logger.info("Starting app.")
    app = App()
    app.run(token=os.environ['TOKEN'])