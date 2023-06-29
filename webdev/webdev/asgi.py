"""
ASGI config for webdev project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webdev.settings')
app = get_asgi_application()

from channels_app.routing import websocket_urlpatterns as ws_url

application = ProtocolTypeRouter({
    'http': app,
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(ws_url)))
})
