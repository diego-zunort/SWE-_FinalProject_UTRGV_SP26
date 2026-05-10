from django.contrib import admin
from .models import Club, ClubMembership, Profile, Event, ChatMessage


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
	list_display = ("name", "category", "meetTimes", "emailContact")
	search_fields = ("name", "desc", "category", "tag1", "tag2")
	list_filter = ("category",)


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
	list_display = ("user", "club", "joined_at")
	search_fields = ("user__username", "club__name")
	list_filter = ("club",)


admin.site.register(Profile)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(ChatMessage)
