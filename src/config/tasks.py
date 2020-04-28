from config.celery import app
from learn_word.services.scraper import Scraper
import logging
logger = logging.getLogger("app")

@app.task()
def scrape_weblio():
    scraper = Scraper()
    scraper.begin()
    return 'おわったよ'

@app.task()
def test():
    import time
    logger.debug("test start")
    time.sleep(10)
    logger.debug("test start")
    return 'end'
