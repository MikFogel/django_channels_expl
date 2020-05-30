from django.conf.urls import url
from .consumers import ChatConsumer, AsyncChatConsumer, BaseSyncConsumer, BaseAsyncConsumer, ChatJsonConsumer

websocket_urls = [
    url(r'^ws/chat/$', ChatJsonConsumer),
]