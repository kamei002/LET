
from django.forms import ModelForm
# from django import forms
from learn_word import models

# from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger("app")


class SettingForm(ModelForm):
    class Meta:
        model = models.WordLearnSetting
        fields = ['learn_num']
