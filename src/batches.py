from learn_word import models as word_models
from account import models as account_models
from tqdm import tqdm
from bs4 import BeautifulSoup

import logging
import requests
import random
import time
logger = logging.getLogger("app")


def calc_learn_order():
    word_list = word_models.EnglishWord.objects.all()
    users = account_models.User.objects.all()
    for word in tqdm(word_list):
        for user in users:
            point = word.calc_learn_order_point(user_id=user.id)
            word.point = point
            word_summary = word_models.WordSummary.find_one(
                user_id=user.id,
                english_word_id=word.id
            )
            word_summary.order = point
            word_summary.save()

def download(link, filename="/static/sounds/test.mp3"):
    # print(f'Download {link}')
    req = requests.get(link)

    with open(filename, 'wb') as f:
        f.write(req.content)

def get_audio():
    word_obj_list = word_models.EnglishWord.objects.filter(audio_path__contains='https://weblio')
    for word_obj in tqdm(word_obj_list):
        link = word_obj.audio_path
        filename = f'/static/sounds/{word_obj.word}.mp3'
        logger.debug(filename)
        download(link=link, filename=filename)
        word_obj.audio_path = filename
        word_obj.save()
        time.sleep(random.random()*10)

def get_img():
    word_obj_list = word_models.EnglishWord.objects.filter(image_path__isnull=True)
    for word_obj in tqdm(word_obj_list):
        word = word_obj.word
        url = f'https://www.shutterstock.com/search/{word}'
        headers = get_scrape_header()
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            imgs = soup.select("img")
            link = imgs[0]['src']
            logger.debug(link)

            filename = f'/static/word-image/{word}.jpg'
            logger.debug(filename)
            download(link=link, filename=filename)
            word_obj.image_path = filename
            word_obj.save()
            time.sleep(random.random()*10)

        except Exception as e:
            logger.exception(f'error_message: {e}')

def get_mean():
    word_obj_list = word_models.EnglishWord.get_scrapable_word()
    for word_obj in tqdm(word_obj_list):
        word = word_obj.word
        url = f'https://ejje.weblio.jp/content/{word}'
        headers = get_scrape_header()
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
        time.sleep(random.random()*10)


def get_synonyms():

    word_obj_list = word_models.EnglishWord.objects.filter(synonyms__isnull=True)

    for word_obj in tqdm(word_obj_list):
        word = word_obj.word
        url = f'https://www.thesaurus.com/browse/{word}'
        headers = get_scrape_header()
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            logger.debug(f"word:{word}")
            synonyms_node = soup.select(".css-18rr30y.etbu2a31")
            # logger.debug(f"synonyms_node:{synonyms_node}")
            synonym_word_id = word_obj.id
            for synonym_node in synonyms_node:
                synonym = synonym_node.string
                english_word = word_models.EnglishWord.objects.filter(word=synonym).first()
                synonym_obj = word_models.Synonyms(
                    synonym_word_id=synonym_word_id,
                    word=synonym,
                    english_word=english_word
                )
                synonym_obj.save()
                # logger.debug(synonym)

        except Exception as e:
            logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')

        time.sleep(random.random()*10)


def get_synonyms_from_oxford():

    word_obj_list = word_models.EnglishWord.objects.filter(synonyms__isnull=True)
    for word_obj in tqdm(word_obj_list):
        word = word_obj.word
        # url = 'https://www.lexico.com/en/definition/groan'
        url = f'https://www.lexico.com/en/definition/{word}'
        headers = get_scrape_header()
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            logger.debug(f"word:{word}")
            synonyms_node = soup.select(".synonyms .exg .syn")
            logger.debug(f"synonyms_node:{synonyms_node}")
            # logger.debug(f"synonyms_node:{soup.select('.exg')}")

            synonym_word_id = word_obj.id
            synonyms = set()
            for synonym_node in synonyms_node:
                synonym_list = synonym_node.string
                for synonym in synonym_list.split(','):
                    synonym = synonym.replace(" ", "")
                    if synonym:
                        synonyms.add(synonym)

            logger.debug(synonyms)
            for synonym in synonyms:
                english_word = word_models.EnglishWord.objects.filter(word=synonym).first()
                synonym_obj = word_models.Synonyms(
                    synonym_word_id=synonym_word_id,
                    word=synonym,
                    english_word=english_word
                )
                synonym_obj.save()

        except Exception as e:
            logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')
        time.sleep(random.random()*10)


def get_scrape_header():
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
    return headers
