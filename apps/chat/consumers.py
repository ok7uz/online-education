import base64
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile

from apps.chat.models import Chat, Message
from apps.chat.serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat = None
        self.user = None
        self.chat_id = None
        self.room_group_name = None

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat = await self.get_chat(self.chat_id)
        self.user = self.scope['user']

        if not self.chat or not self.scope['user'].is_authenticated:
            await self.close()

        self.room_group_name = 'chat_%s' % self.chat_id
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get('message', None)
        media = text_data_json.get('media', None)
        media_type = text_data_json.get('media_type', None)
        if message_text or media:
            if media:
                file_str, file_name = media['data'], media['file_name']
                media = ContentFile(
                    base64.b64decode(file_str), name=file_name
                )
            message = await Message.objects.acreate(
                chat=self.chat,
                sender=self.user,
                content=message_text,
                media=media,
                media_type=media_type
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    async def chat_message(self, event):
        message_serializer = MessageSerializer(event['message'], context={'user': self.user})
        await self.send(text_data=json.dumps({
            'message': message_serializer.data,
            'user': self.user.username
        }))

    @staticmethod
    async def get_chat(chat_id):
        try:
            return await Chat.objects.aget(id=chat_id)
        except Chat.DoesNotExist:
            return None
