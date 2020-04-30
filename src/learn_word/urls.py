from django.urls import path
from . import views
from rest_framework import routers

app_name = 'word'
router = routers.DefaultRouter()
urlpatterns = [
    path('learn', views.learn),
    path('learn/result', views.learn_result),
    path('list', views.WordList.as_view()),
    path('api/star', views.Star.as_view()),
    path('api/unknown-word', views.UnknownWord.as_view()),
    path('category', views.category),

]
