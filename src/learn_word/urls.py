from django.urls import path
from . import views
from rest_framework import routers

app_name = 'word'
router = routers.DefaultRouter()
urlpatterns = [
    path('', views.Learn.as_view()),
    path('list', views.WordList.as_view()),
    path('api/star', views.Star.as_view()),
    path('api/unknown-word', views.UnknownWord.as_view()),
    path('category', views.category),
    path('category/<int:category_id>/learn', views.learn_category),
    path('api/scrap', views.scrap),

]
