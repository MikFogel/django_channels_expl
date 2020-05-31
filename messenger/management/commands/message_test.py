import time
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()
        for i in range(10):
            async_to_sync(channel_layer.group_send) (
                "dribin",
                {
                    "type": "chat.message",
                    'text': "Message outside concsumer {}".format(i)
                }
            )
            time.sleep(1)