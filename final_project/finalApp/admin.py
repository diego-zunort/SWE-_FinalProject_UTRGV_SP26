from django.contrib import admin
from .models import Club, ClubMembership, Profile, Event, ChatMessage

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "meetTimes", "emailContact", "image")
    search_fields = ("name", "desc", "category", "tag1", "tag2")
    list_filter = ("category",)

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "club", "is_admin", "joined_at")
    search_fields = ("user__username", "club__name")
    list_filter = ("club", "is_admin")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "club", "start_time", "end_time", "location")
    search_fields = ("title", "description", "club__name", "location")
    list_filter = ("club", "start_time")
    date_hierarchy = "start_time"

admin.site.register(Profile)
admin.site.register(ChatMessage)
