from django.urls import path
from . import views
from rest_framework import routers

app_name = 'word'
router = routers.DefaultRouter()
urlpatterns = [
    path('list', views.WordList.as_view()),
    path('api/star', views.Star.as_view()),
    path('api/unknown-word', views.UnknownWord.as_view()),
    path('setting', views.Setting.as_view()),
    path('learn', views.learn),
    path('learn/result', views.learn_result),
    path('category', views.category),
]
