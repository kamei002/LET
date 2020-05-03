from django.db import models
from account.models.users import User
from django.utils import timezone
from django.db.models import Q

import datetime
import logging
logger = logging.getLogger("app")

UNKNOWN_POINT = -11
KNOWN_POINT = 10

def show_study_words(user_id, limit=100, category_id=None, is_checked=0):
    sql = "SELECT english_word.* FROM english_word " \
        + "LEFT JOIN word_summary ON english_word.id = word_summary.english_word_id " \
        + f"AND word_summary.user_id = {user_id} "

    sql += f"WHERE 1=1 "
    if category_id:
        sql += f"AND english_word.category_id = {category_id} "

    if is_checked:
        sql += f"AND word_summary.is_checked = true "

    sql += f"ORDER BY word_summary.order LIMIT {limit}"

    word_list = EnglishWord.objects.raw(sql)
    logger.debug(word_list)

    return word_list


class WordCategory(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True)
    image_path = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'word_category'

    def get_category(path="/"):
        result = WordCategory.objects.filter(path=path)
        return result

    def get_children(self):
        search_path = f'{self.path}{self.id}/'
        result = WordCategory.objects.filter(path__contains=search_path)
        return result

    def has_word_relation(self):
        result = self.words.exists()
        return result

    def has_word_relations(self):
        if self.has_word_relation():
            return True
        child_categories = self.get_children()
        for category in child_categories:
            if category.has_word_relation():
                return True
        return False

class EnglishWord(models.Model):
    word = models.CharField(max_length=255)
    mean = models.CharField(max_length=255, null=True)
    audio_path = models.CharField(max_length=255, null=True)
    image_path = models.CharField(max_length=255, null=True)
    order = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(WordCategory, null=True, on_delete=models.SET_NULL, related_name='words')

    class Meta:
        db_table = 'english_word'

    def get_scrapable_word():
        return EnglishWord.objects.filter(
            Q(mean__isnull=True) | Q(audio_path__isnull=True)
        )

    def calc_learn_order_point(self, user_id):
        word_logs = WordLog.objects.filter(english_word_id=self.id, user_id=user_id)
        point = 0
        known_count = word_logs.filter(is_unknown=False).count()
        point += known_count * KNOWN_POINT

        unknown_count = word_logs.filter(is_unknown=True).count()
        point += unknown_count * UNKNOWN_POINT

        return point


class WordSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_summaries')
    english_word = models.ForeignKey(EnglishWord, on_delete=models.CASCADE, related_name='word_summary')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    display_count = models.IntegerField(default=0)
    is_checked = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'word_summary'

    def find_one(user_id, english_word_id):
        result = WordSummary.objects.filter(english_word_id=english_word_id).first()
        if result is None:
            result = WordSummary(user_id=user_id, english_word_id=english_word_id)
            result.save()
        return result

    def count_up(self):
        self.display_count += 1
        self.save()

class WordLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_logs')
    english_word = models.ForeignKey(EnglishWord, on_delete=models.CASCADE, related_name='word_logs')
    is_unknown = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'word_log'

    def create(user_id, english_word_id):

        result = WordLog(user_id=user_id, english_word_id=english_word_id)
        word_summary = result.get_word_summary()
        word_summary.count_up()
        result.save()
        return result

    def get_learn_result(user_id, limit):
        result = WordLog.objects.filter(
            user_id=user_id
        ).order_by(
            'created_at'
        ).reverse(

        ).select_related('english_word')[:limit]
        logger.debug(result.query)
        return result

    def number_of_today_study(user_id):
        result = WordLog.objects.filter(
            user_id=user_id,
            created_at__gt=datetime.date.today()
        )
        return result.count()

    def mark_unknown(self):
        self.is_unknown = True
        self.save()
        word_summary = self.get_word_summary()
        word_summary.order += UNKNOWN_POINT
        word_summary.save()

    def mark_known(self):
        self.is_unknown = False
        self.save()
        word_summary = self.get_word_summary()
        word_summary.order += KNOWN_POINT
        word_summary.save()

    def get_word_summary(self):
        return WordSummary.find_one(
            user_id=self.user_id,
            english_word_id=self.english_word_id
        )

class WordLearnSetting(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    learn_num = models.IntegerField(default=100)
    default_unknown = models.BooleanField(default=False)

    class Meta:
        db_table = 'word_learning_setting'

    def find_by_user_id(user_id):
        setting = WordLearnSetting.objects.filter(user_id=user_id).first()
        if setting is None:
            setting = WordLearnSetting(user_id=user_id)
            setting.save()
        return setting
