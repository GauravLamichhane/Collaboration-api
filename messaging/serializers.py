from rest_framework import serializers
from .models import Message, DirectMessage, Reaction, Attachment
from accounts.serializers import UserSerializer


class ReactionSerializer(serializers.ModelSerializer):
    """Serializer for reactions"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'emoji', 'created_at']
        read_only_fields = ['id', 'created_at']


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for attachments"""
    
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'file', 'filename', 'file_type', 'file_size',
            'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'filename', 'file_type', 'file_size', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for channel messages"""
    
    sender = UserSerializer(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'channel', 'sender', 'content', 'parent',
            'reactions', 'attachments', 'reply_count',
            'edited', 'pinned', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender', 'edited', 'created_at', 'updated_at']
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class DirectMessageSerializer(serializers.ModelSerializer):
    """Serializer for direct messages"""
    
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    recipient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DirectMessage
        fields = [
            'id', 'sender', 'recipient', 'recipient_id', 'content',
            'reactions', 'attachments', 'read', 'read_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender', 'read', 'read_at', 'created_at', 'updated_at']
    
    def validate_recipient_id(self, value):
        # Can't send message to yourself
        if value == self.context['request'].user.id:
            raise serializers.ValidationError("Cannot send message to yourself")
        return value