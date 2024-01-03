import logging
from time import sleep

from tenacity import retry, wait_fixed, before_sleep_log

from src.bot import main
from src.bot import first_run

from src.secret import LOGGING_ENABLED


def configure_logging():
    logging.basicConfig(
        filename='bot.log',
        filemode='w',
        level=logging.ERROR,
        format='%(name)s - %(levelname)s - %(message)s'
    )
    if not LOGGING_ENABLED:
        logging.disable(logging.CRITICAL)
    return logging.getLogger(__name__)


logger = configure_logging()


@retry(wait=wait_fixed(10), before_sleep=before_sleep_log(logger, logging.ERROR, exc_info=True))
def run():
    while True:
        print("run")
        main(production=True)
        sleep(10)


# execute the first_run function just ONCE to create the database with the latest alert ID
# and prevent bot responding ALL old messages.
# comment run() function at bottom before run first_run function.

# first_run(production=True)
run()
