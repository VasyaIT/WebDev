from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_channel/', views.create_channel, name='create_channel'),
    path('channels/<slug:slug>/', views.detail_channel, name='detail_channel'),
    path('tag/<slug:tag_slug>/', views.index, name='detail_tag'),
]
