"""
ASGI config for HumanOS.

Supports HTTP + WebSocket (for Nervous System real-time signals).
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()

# When Django Channels is installed, upgrade to support WebSocket:
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(URLRouter([...])),
# })
