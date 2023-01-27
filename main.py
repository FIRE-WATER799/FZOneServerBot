import logging
import os 
from sys import gettrace

import coloredlogs

from src.Bot import FzBot


def setup():
    logger = logging.getLogger()

    if gettrace() is None:
        token = ''
        logger.info("Logging in as User...")
        bot = FzBot()

        bot.run(str(token))
    else:
        coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(evelname)-1s]| %(message)s", )
        logger.info("Running in DEBUG mode")
        token=''
        bot = FzBot()

        bot.run(token)


if __name__ == "__main__":
    setup()
