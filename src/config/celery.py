# celery_handson/celery_handson/celery.py
import os
from celery import Celery
# from django.conf import settings

import logging
logger = logging.getLogger("app")

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
app = Celery('config')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks()


# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# app = Celery('config')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()
