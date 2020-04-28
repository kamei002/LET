from learn_word import models as word_models
from account import models as account_models
from tqdm import tqdm
import logging
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
