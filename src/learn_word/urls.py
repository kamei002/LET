from django.urls import path
from . import views
from rest_framework import routers

app_name = 'word'
router = routers.DefaultRouter()
urlpatterns = [
    path('', views.Learn.as_view()),
    path('list', views.WordList.as_view()),
]
