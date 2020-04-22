from django.db import models
from account.models.users import User
from django.utils import timezone
from django.db.models import Q

import logging
logger = logging.getLogger("app")


def show_study_words(user_id):
    logger.debug(user_id)
    user = User.objects.get(pk=user_id)
    logger.debug(user)
    setting = WordLearnSetting.find_by_user_id(user_id=user_id)
    logger.debug(setting)
    limit = setting.display_num
    return limit


class WordCategory(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='children')

    class Meta:
        db_table = 'word_category'


class EnglishWord(models.Model):
    word = models.CharField(max_length=255)
    mean = models.CharField(max_length=255, null=True)
    audio_path = models.CharField(max_length=255, null=True)
    is_checked = models.BooleanField(default=False)
    order = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_displayed_at = models.DateTimeField(null=True, default=timezone.now)
    category = models.ForeignKey(WordCategory, null=True, on_delete=models.SET_NULL, related_name='word_audios')

    class Meta:
        db_table = 'english_word'

    def get_scrapable_word():
        return EnglishWord.objects.filter(
            Q(mean__isnull=True) | Q(audio_path__isnull=True)
        )


class WordLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_logs')
    english_word = models.ForeignKey(EnglishWord, on_delete=models.CASCADE, related_name='word_logs')
    is_unknown = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'word_log'


class WordLearnSetting(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    display_num = models.IntegerField(default=10)
    default_unknown = models.BooleanField(default=False)

    class Meta:
        db_table = 'word_learning_setting'

    def find_by_user_id(user_id):
        setting = WordLearnSetting.objects.filter(user_id=user_id).first()
        if setting is None:
            setting = WordLearnSetting(user_id=user_id)
            setting.save()
        return setting
