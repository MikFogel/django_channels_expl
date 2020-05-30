from channels.routing import ProtocolTypeRouter, URLRouter
from messenger.routing import websocket_urls

application = ProtocolTypeRouter({
    "websocket": URLRouter(
        websocket_urls,
    )
})
