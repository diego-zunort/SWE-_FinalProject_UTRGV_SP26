from django.contrib import admin
from .models import ChatMessage
from .models import Event
from .models import Club

# Register your models here.
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(ChatMessage)