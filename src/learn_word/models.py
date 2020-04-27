from django.db import models
from account.models.users import User
from django.utils import timezone
from django.db.models import Q

import logging
logger = logging.getLogger("app")


def show_study_words(limit=100, category_id=None):
    word_list = EnglishWord.objects.all()

    if category_id:
        category = WordCategory.objects.get(pk=category_id)
        category_ids = set(category.get_children().values_list('id', flat=True))
        category_ids.add(category_id)
        word_list = word_list.filter(category_id__in=category_ids)

    word_list = word_list.order_by(
        "word_summary__display_count"
    )[:limit]

    return word_list


class WordCategory(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True)

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


class WordSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_summaries')
    english_word = models.ForeignKey(EnglishWord, on_delete=models.CASCADE, related_name='word_summary')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    display_count = models.IntegerField(default=0)
    is_checked = models.BooleanField(default=False)

    class Meta:
        db_table = 'word_summary'

    def find_one(user_id, english_word_id):
        result = WordSummary.objects.filter(english_word_id=english_word_id).first()
        if result is None:
            result = WordSummary(user_id=user_id, english_word_id=english_word_id)
            result.save()
        return result

class WordLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_logs')
    english_word = models.ForeignKey(EnglishWord, on_delete=models.CASCADE, related_name='word_logs')
    is_unknown = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'word_log'

    def get_one(user_id, english_word_id):
        result = WordLog(user_id=user_id, english_word_id=english_word_id)
        result.save()
        return result


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
