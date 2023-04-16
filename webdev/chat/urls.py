from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('<str:room_name>/', views.chat_detail, name='chat_detail'),

]
