from django.contrib import admin
from workspaces.models import Workspace, WorkspaceMember, Channel, ChannelMember

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'created_at']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace', 'channel_type', 'created_by']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(WorkspaceMember)
admin.site.register(ChannelMember)