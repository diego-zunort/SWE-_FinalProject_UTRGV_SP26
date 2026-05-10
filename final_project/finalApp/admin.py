from django.contrib import admin
from .models import ChatMessage
from .models import Event
from .models import Club

admin.site.register(Club)
admin.site.register(ChatMessage)
admin.site.register(Event)
