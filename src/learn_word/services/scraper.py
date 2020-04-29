from bs4 import BeautifulSoup
import requests
from learn_word import models
import time
from itertools import cycle
import logging
logger = logging.getLogger("app")

class Scraper:

    def get_weblio(self, word_obj, proxy=None):
        word = word_obj.word
        url = f'https://ejje.weblio.jp/content/{word}'
        proxies = {
            "http": proxy,
            "https": proxy,
        }
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
        res = requests.get(url, headers=headers, proxies=proxies)
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
        time.sleep(3)

    def get_proxies(self):
        # url = 'http://spys.one/free-proxy-list/JP/'
        url = 'https://free-proxy-list.net/'
        res = requests.get(url)

        soup = BeautifulSoup(res.text, 'html.parser')

        try:
            ips = soup.select('#proxylisttable > tbody > tr > td:nth-child(1)')
            ports = soup.select('#proxylisttable > tbody > tr > td:nth-child(2)')
            proxies = []
            for i, ip in enumerate(ips):
                proxy = f'{ips[i].string}:{ports[i].string}'
                proxies.append(proxy)

        except Exception as e:
            logger.exception(f'error_message: {e}')
            proxies = []
        logger.debug(proxies)

        return proxies

    def begin(self):
        words = models.EnglishWord.get_scrapable_word()
        # proxies = self.get_proxies()
        # proxy_pool = cycle(proxies)
        logger.debug(words)
        for word_obj in words:
            try:
                # proxy = next(proxy_pool)
                self.get_weblio(word_obj)
            except Exception as e:
                logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')

    def test(self):
        proxies = self.get_proxies()
        proxy_pool = cycle(proxies)
        for i in range(100):
            try:
                proxy = next(proxy_pool)
                self.ipcheck(proxy=proxy)
            except Exception as e:
                logger.exception(f'error_message: {e}')

    def ipcheck(self, proxy=None):
        url = 'https://httpbin.org/ip'
        try:
            print(proxy)
            response = requests.get(url, proxies={"http": proxy, "https": proxy})
            print(response.json())
        except Exception as e:
            print(e)
