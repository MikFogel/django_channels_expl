import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
from .models import Online


#  self.scope = аналог request в django channels
#  словарь, который хранит соединение


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)
        print (code)

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                "type": "chat.message",
                'text': text_data
            }
        )

    def chat_message(self, event):
        print (event)
        self.send(text_data=event['text'])


class NoRedisChatConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, code):
        print (code)

    def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads((text_data))

        message = json_data['message']
        print(message)

        self.send(text_data * int(message))


class ChatJsonConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, code):
        print (code)

    def receive_json(self, content, **kwargs):
        self.send_json(content=content)

    @classmethod
    def encode_json(cls, content):
        return super().encode_json(content)

    @classmethod
    def decode_json(cls, text_data):
        return super().decode_json(text_data)


class ChatAsyncJsonConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()

    def disconnect(self, code):
        print (code)

    async def receive_json(self, content, **kwargs):
        await self.send_json(content=content)

    @classmethod
    def encode_json(cls, content):
        return super().encode_json(content)

    @classmethod
    def decode_json(cls, text_data):
        return super().decode_json(text_data)


class AsyncChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await database_sync_to_async(self.create_online) ()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.delete_online()
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        print (code)

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat.message",
                "text": text_data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=event['text'])
        print (event)

    def create_online(self):
        new, _ = Online.objects.get_or_create(name=self.channel_name)

    @database_sync_to_async
    def delete_online(self):
        Online.objects.filter(name=self.channel_name).delete()

class BaseSyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        self.send({
            "type": "websocket.accept"
        })

    def websocket_receive(self, event):
        import datetime
        self.send({
            "type": "websocket.send",
            "text": str(datetime.datetime.now())
        })

    def websocket_disconnect(self):
        raise StopConsumer()


class BaseAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_disconnect(self):
        raise StopConsumer()

    async def websocket_receive(self, event):
        import datetime
        await self.send({
            "type": "websocket.send",
            "text": str(datetime.datetime.now())
        })

