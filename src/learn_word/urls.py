from django.urls import path
from . import views
from rest_framework import routers

app_name = 'word'
router = routers.DefaultRouter()
urlpatterns = [
    path('', views.WordList.as_view()),
]
