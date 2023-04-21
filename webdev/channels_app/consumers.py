import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Message, Channel, User


class ChannelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        user = self.scope['user']
        await self.create_current_user(user, self.room_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        user = self.scope['user']

        await self.delete_current_user(user, self.room_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']

        await self.save_message(username, room, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.strip(),
                'username': username,
                'room': room
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        room = event['room']

        await self.send(json.dumps({
            'message': message.strip(),
            'username': username,
            'room': room
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        channel = Channel.objects.select_related('tag', 'author').get(slug=room)
        if message.strip() == '':
            return
        Message.objects.create(user=user, channel=channel, text=message)

    @sync_to_async
    def create_current_user(self, user, room):
        channels = Channel.objects.select_related('tag', 'author').get(slug=room)
        channels.current_users.add(user)

    @sync_to_async
    def delete_current_user(self, user, room):
        channels = Channel.objects.select_related('tag', 'author').get(slug=room)
        channels.current_users.remove(user)
