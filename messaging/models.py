from django.db import models
from django.conf import settings
from workspaces.models import Channel

class Message(models.Model):
    """Messages in channels"""
    
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    edited = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['channel', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class DirectMessage(models.Model):
    """Direct messages between users"""
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_direct_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_direct_messages'
    )
    content = models.TextField()
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}"


class Reaction(models.Model):
    """Emoji reactions to messages"""
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions',
        null=True,
        blank=True
    )
    direct_message = models.ForeignKey(
        DirectMessage,
        on_delete=models.CASCADE,
        related_name='reactions',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    emoji = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['message', 'user', 'emoji'],
            ['direct_message', 'user', 'emoji']
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.emoji}"


class Attachment(models.Model):
    """File attachments for messages"""
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True,
        blank=True
    )
    direct_message = models.ForeignKey(
        DirectMessage,
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True,
        blank=True
    )
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename