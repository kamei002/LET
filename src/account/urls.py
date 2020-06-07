from django.urls import path
from . import views
from rest_framework import routers

app_name = 'account'
router = routers.DefaultRouter()
urlpatterns = [
    # path('create/', views.Signup.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('dashboard/', views.Dashboard.as_view()),
]
