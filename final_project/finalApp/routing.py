from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/clubs/<str:club_slug>/chat/", consumers.ChatConsumer.as_asgi()),
    path("ws/general/chat/", consumers.GeneralChatConsumer.as_asgi()),
]
