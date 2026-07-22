from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "short_content", "created_at")
    list_filter = ("room",)
    search_fields = ("user__username", "content")
    date_hierarchy = "created_at"

    @admin.display(description="Message")
    def short_content(self, obj):
        return obj.content[:60]
