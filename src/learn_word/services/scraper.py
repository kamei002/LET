from bs4 import BeautifulSoup
import requests
from learn_word import models

import logging
logger = logging.getLogger("app")

class Scraper:

    def get_weblio(self, word_obj):
        word = word_obj.word
        url = f'https://ejje.weblio.jp/content/{word}'
        headers = {
            'user-agent': 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'referer': 'https://www.google.com/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
        }
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            mean = soup.select("#summary > div.summaryM.descriptionWrp > table > tbody > tr > td.content-explanation.ej")[0].string
        except Exception as e:
            logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')
            mean = ' '
        logger.debug(mean)
        word_obj.mean = mean

        try:
            audio_path = soup.select("#audioDownloadPlayUrl")[0]['href']
        except Exception as e:
            logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')
            audio_path = ' '
        logger.debug(audio_path)
        word_obj.audio_path = audio_path
        word_obj.save()
        # time.sleep(1)

    def begin(self):
        words = models.EnglishWord.get_scrapable_word()
        logger.debug(words)
        for word_obj in words:
            try:
                self.get_weblio(word_obj)
            except Exception as e:
                logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')
