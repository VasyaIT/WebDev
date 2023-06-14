from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_channel, name='create_channel'),
    path('edit/', views.create_channel, name='edit_channel'),
    path('delete/', views.delete_channel, name='delete_channel'),
    path('channels/<slug:slug>/', views.detail_channel, name='detail_channel'),
    path('tag/<slug:tag_slug>/', views.index, name='detail_tag'),
]
