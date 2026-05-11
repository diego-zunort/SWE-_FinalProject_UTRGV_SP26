import json
from json import JSONDecodeError

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Club, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.club_slug = self.scope["url_route"]["kwargs"]["club_slug"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.club_id = await self.get_joined_club_id()
        if self.club_id is None:
            await self.close(code=4003)
            return

        self.club_group_name = f"chat_{self.club_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.club_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, "club_group_name"):
            await self.channel_layer.group_discard(
                self.club_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except JSONDecodeError:
            return

        message = data.get("message", "").strip()
        if not message:
            return

        saved_message = await self.save_message(message)

        author_username = self.user.username

        # Send message to room group
        await self.channel_layer.group_send(
            self.club_group_name,
            {
                "type": "chat_message",
                "message": saved_message["message"],
                "author": author_username,
                "timestamp": saved_message["timestamp"],
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        author = event["author"]
        timestamp = event["timestamp"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "author": author,
            "timestamp": timestamp,
        }))

    @database_sync_to_async
    def get_joined_club_id(self):
        return (
            Club.objects
            .filter(slug=self.club_slug, memberships__user_id=self.user.id)
            .values_list("id", flat=True)
            .first()
        )

    @database_sync_to_async
    def save_message(self, message):
        chat_message = ChatMessage.objects.create(
            club_id=self.club_id,
            author_id=self.user.id,
            message=message,
        )
        return {
            "message": chat_message.message,
            "timestamp": chat_message.timestamp.strftime("%I:%M %p").lstrip("0"),
        }
