from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'status', 'last_seen']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'username']