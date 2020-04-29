from learn_word import models as word_models
from account import models as account_models
from tqdm import tqdm
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
            word_summary.order = -1 * point
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
