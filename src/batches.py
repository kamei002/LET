from learn_word import models as word_models
from account import models as account_models
from tqdm import tqdm
from bs4 import BeautifulSoup

from django.db import connection, transaction

import pandas as pd
import logging
import requests
import random
import time
from unidecode import unidecode
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
    word_obj_list = word_models.EnglishWord.objects.exclude(audio_path__isnull=True).exclude(audio_path__startswith='/static')
    for word_obj in tqdm(word_obj_list):
        logger.debug(f"id:{word_obj.id}, word:{word_obj.word}")
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
        logger.debug(f"id:{word_obj.id}, word:{word_obj.word}")
        word = word_obj.word
        url = f'https://www.shutterstock.com/search/{word}'
        headers = get_scrape_header()
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            imgs = soup.select("img")
            link = imgs[0]['src']
            logger.debug(link)

            # filename = f'/static/word-image/{word}.jpg'
            # logger.debug(filename)
            # download(link=link, filename=filename)

        except Exception as e:
            logger.exception(f'error_message: {e}')
            link = ' '

        word_obj.image_path = link
        word_obj.save()
        time.sleep(random.random()*10)

def scrape_weblio():
    word_obj_list = word_models.EnglishWord.get_scrapable_word()
    for word_obj in tqdm(word_obj_list):
        logger.debug(f"id:{word_obj.id}, word:{word_obj.word}")
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
            logger.debug(audio_path)
            # filename = f'/static/sounds/{word}.mp3'
            # download(link=audio_path, filename=audio_path)
        except Exception as e:
            logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')
            # filename = ' '
            audio_path = ' '
        word_obj.audio_path = audio_path
        word_obj.save()
        time.sleep(random.random()*10)

def scrape_oxford():

    word_obj_list = word_models.EnglishWord.objects.filter(defines__isnull=True)
    for word_obj in tqdm(word_obj_list):
        logger.debug(f"id:{word_obj.id}, word:{word_obj.word}")
        word = word_obj.word
        # url = 'https://www.lexico.com/en/definition/prove'
        url = f'https://www.lexico.com/en/definition/{word}'
        headers = get_scrape_header()
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            word_class_sections = soup.select("section.gramb")

            logger.debug(f"word:{word}")
            # logger.debug(f"word_class_sections:{word_class_sections}\n\n\n")

            for word_class_section in word_class_sections:
                _scrape_oxford_word_section(word_obj=word_obj, word_class_section=word_class_section)

        except Exception as e:
            logger.exception(f'word_id:{word_obj.id} word:{word_obj.word} error_message: {e}')
        time.sleep(random.random()*10)


def _scrape_oxford_word_section(word_obj, word_class_section):
    try:
        # logger.debug(f"word_class_section:{word_class_section}\n\n\n")
        word_class = word_class_section.select(".pos")
        if not word_class:
            return
        word_class = word_class[0].string
        logger.debug(f"word_class:{word_class}")

        mean_nodes = word_class_section.select("ul li div.trg")
        logger.debug(f"mean_nodes:{mean_nodes}\n\n\n")

        for mean_node in mean_nodes:
            _scrape_oxford_mean_node(word_obj=word_obj, mean_node=mean_node, word_class=word_class)
    except Exception as e:
        logger.exception(f'word_id:{word_obj.id} word_class_section:{word_class_section} error_message: {e}')

def _scrape_oxford_mean_node(word_obj, mean_node, word_class=''):
    try:
        # logger.debug(f"mean_node:{mean_node}\n\n\n")
        mean = mean_node.select('p:nth-child(1) span.ind')
        if not mean:
            logger.info(f"mean not found!!!!!:{mean_node}\n\n\n")
            return
        mean = mean[0].string
        # logger.debug(f"mean:{mean}")

        synonyms_node = mean_node.select(".synonyms .exg .syn")
        # logger.debug(f"synonyms_node:{synonyms_node}\n\n\n")

        define_obj = word_models.Define(
            english_word_id=word_obj.id,
            meaning_en=mean,
            parent=None,
            word_class=word_class,
        )
        define_obj.save()
        logger.debug(f"save define. id:{define_obj.id} meaning:{mean}")
        define_id = define_obj.id

        _save_oxford_synonyms(synonyms_node=synonyms_node, define_id=define_id)

        # children_node = mean_node.select('li.subSense')
        # logger.debug(f"children_node:{children_node}\n\n\n")
        # for child_node in children_node:
        #     try:
        #         child_mean = child_node.select('span.ind')
        #         if not child_mean:
        #             logger.info(f"child_mean not Found children_node:{children_node}\n\n")
        #             continue
        #         child_mean = child_mean[0].string

        #         child_define_obj = word_models.Define(
        #             english_word_id=word_obj.id,
        #             meaning_en=child_mean,
        #             parent=define_obj,
        #             word_class=word_class,
        #         )
        #         child_define_obj.save()
        #         logger.debug(f"save define child. id:{child_define_obj.id} meaning:{child_mean} parent_id:{define_id}")

        #         synonyms_node = child_node.select(".synonyms .exg .syn")
        #         _save_oxford_synonyms(synonyms_node=synonyms_node, define_id=child_define_obj.id)
        #     except Exception as e:
        #         logger.exception(f'word_id:{word_obj.id} child_node:{child_node} error_message: {e}')

    except Exception as e:
        logger.exception(f'word_id:{word_obj.id} mean_node:{mean_node} error_message: {e}')

def _save_oxford_synonyms(synonyms_node, define_id):
    try:
        # synonyms = set()
        for synonym_node in synonyms_node:
            synonym_list = synonym_node.string
            for synonym in synonym_list.split(','):
                synonym = synonym.replace(" ", "")
                if synonym:
                    # synonyms.add(synonym)
                    logger.debug(f"save_synonym word:{synonym} define_id:{define_id}")
                    english_word = word_models.EnglishWord.objects.filter(word=synonym).first()
                    synonym_obj = word_models.MeaningSynonym(
                        word=synonym,
                        define_id=define_id,
                        english_word=english_word,
                    )
                    synonym_obj.save()
    except Exception as e:
        logger.exception(f'synonyms_node:{synonyms_node} error_message: {e}')

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

def update_meaning_ja(csv_path='define.csv'):

    df = pd.read_csv(csv_path)
    sql = 'UPDATE define SET meaning_ja = (CASE id '
    id_list = []
    for (define_id, meaning_ja) in df[['id', 'meaning_ja']].values:
        define_id = int(define_id)
        if not meaning_ja:
            continue
        sql += f" WHEN {define_id} THEN '{meaning_ja}' "
        id_list.append(str(define_id))
    str_id = ','.join(id_list)
    sql += f" END) WHERE id IN({str_id})"

    cursor = connection.cursor()
    cursor.execute(sql)
    transaction.atomic()

def register_unregistered_synonym_word(user_id=1):

    word_obj = word_models.EnglishWord.objects.all().values_list('word', flat=True)
    word_set = set([unidecode(w.lower()) for w in word_obj])
    synonym_obj = word_models.MeaningSynonym.objects.all().values_list('word', flat=True)
    synonym_set = set([unidecode(w.lower()) for w in synonym_obj])
    register_set = synonym_set - word_set
    word_obj_list = []
    for word in register_set:
        word_obj = word_models.EnglishWord(
            word=word,
            created_by_id=user_id
        )
        word_obj_list.append(word_obj)
    word_models.EnglishWord.objects.bulk_create(word_obj_list)

def set_synonym_relation():
    synonym_obj = word_models.MeaningSynonym.objects.filter(english_word_id__isnull=True).filter()
    update_objs = []
    for synonym in tqdm(synonym_obj):
        word_obj = word_models.EnglishWord.objects.filter(word=synonym.word).first()
        if not word_obj:
            print(f'not found: {synonym.word}')
            continue
        synonym.english_word = word_obj
        # synonym.save()
        update_objs.append(synonym)

    word_models.MeaningSynonym.objects.bulk_update(update_objs, ['english_word_id'])
