from django.db import models
from django.conf import settings

"""
Workspace	Represents a team or organization (like a Slack workspace).
WorkspaceMember	Tracks which users belong to which workspace and their role.
Channel	Represents a communication channel inside a workspace (like Slack channels).
ChannelMember	Tracks which users belong to which channel, and their activity info.

"""
class Workspace(models.Model):
  #Team/organization WorkSpace
  name = models.CharField(max_length=100)
  slug = models.SlugField(unique=True)
  description = models.TextField(blank=True)
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,#Link to our custom Model
    on_delete=models.CASCADE,
    related_name='owned_workspaces'#let you access all workspaces a owner owns via user.owned_workspaces.all()
  )
members = models.ManyToManyField(
  settings.AUTH_USER_MODEL,
  through='WorkspaceMember',#instead of manytomany field you use this to store extra info like roles.
  related_name='Workspace'
)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

class Meta:
  ordering = ['-created_at']

def __str__(self):
  return self.name


class WorkspaceMember(models.Model):
    """Workspace membership with roles"""
    
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    )
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['workspace', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.workspace.name} ({self.role})"


class Channel(models.Model):
    """Communication channels within workspace"""
    
    CHANNEL_TYPE_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='channels'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    channel_type = models.CharField(
        max_length=10,
        choices=CHANNEL_TYPE_CHOICES,
        default='public'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_channels'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChannelMember',
        related_name='channels'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['workspace', 'slug']
        ordering = ['name']
    
    def __str__(self):
        return f"#{self.name} ({self.workspace.name})"


class ChannelMember(models.Model):
    """Channel membership"""
    
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['channel', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.email} in {self.channel.name}"