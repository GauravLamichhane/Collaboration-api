from django.contrib import admin
from .models import Message, DirectMessage, Reaction, Attachment

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'channel', 'content_preview', 'created_at']
    list_filter = ['created_at', 'edited', 'pinned']
    
    def content_preview(self, obj):
        return obj.content[:50]

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'read', 'created_at']
    list_filter = ['read', 'created_at']

admin.site.register(Reaction)
admin.site.register(Attachment)