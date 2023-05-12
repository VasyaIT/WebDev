from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", consumers.ChannelConsumer.as_asgi()),
]
