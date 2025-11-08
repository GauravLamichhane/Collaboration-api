from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from utils.throttling import MessageRateThrottle
from .models import Message, DirectMessage, Reaction, Attachment
from .serializers import (
    MessageSerializer,
    DirectMessageSerializer,
    ReactionSerializer,
    AttachmentSerializer
)
from workspaces.models import Channel, ChannelMember


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for channel messages"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [MessageRateThrottle]

    def get_queryset(self):
        channel_id = self.request.query_params.get('channel')
        
        # Get messages from channels user is a member of
        queryset = Message.objects.filter(
            channel__members=self.request.user
        )
        
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        
        return queryset.select_related('sender', 'channel').order_by('created_at')

    def perform_create(self, serializer):
        # Verify user is channel member
        channel_id = self.request.data.get('channel')
        channel = get_object_or_404(Channel, id=channel_id)
        
        if not channel.members.filter(id=self.request.user.id).exists():
            raise PermissionError("You must be a channel member to send messages")
        
        serializer.save(sender=self.request.user)
        
        # Invalidate message cache for this channel
        cache.delete_pattern(f"*channel_messages:{channel_id}*")

    def perform_update(self, serializer):
        # Only allow sender to edit
        if serializer.instance.sender != self.request.user:
            raise PermissionError("You can only edit your own messages")
        
        serializer.save(edited=True)

    def perform_destroy(self, instance):
        # Only allow sender to delete
        if instance.sender != self.request.user:
            raise PermissionError("You can only delete your own messages")
        instance.delete()

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add reaction to message"""
        message = self.get_object()
        emoji = request.data.get('emoji')
        
        if not emoji:
            return Response(
                {'error': 'emoji is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reaction, created = Reaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )
        
        if created:
            return Response(
                ReactionSerializer(reaction).data,
                status=status.HTTP_201_CREATED
            )
        else:
            # Remove reaction if already exists (toggle behavior)
            reaction.delete()
            return Response(
                {'message': 'Reaction removed'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin/unpin message"""
        message = self.get_object()
        
        # Check if user has permission (channel member)
        if not message.channel.members.filter(id=request.user.id).exists():
            return Response(
                {'error': 'Must be channel member'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.pinned = not message.pinned
        message.save()
        
        return Response({
            'pinned': message.pinned,
            'message': 'Message pinned' if message.pinned else 'Message unpinned'
        })

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """Get message thread (replies)"""
        message = self.get_object()
        replies = Message.objects.filter(parent=message).order_by('created_at')
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search messages"""
        query = request.query_params.get('q', '')
        channel_id = request.query_params.get('channel')
        
        if len(query) < 3:
            return Response(
                {'error': 'Query must be at least 3 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            content__icontains=query
        )
        
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        
        serializer = self.get_serializer(queryset[:50], many=True)
        return Response(serializer.data)


class DirectMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for direct messages"""
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.request.query_params.get('user')
        
        # Get messages where user is sender or recipient
        queryset = DirectMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )
        
        if other_user_id:
            queryset = queryset.filter(
                Q(sender_id=other_user_id) | Q(recipient_id=other_user_id)
            )
        
        return queryset.select_related('sender', 'recipient').order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark message as read"""
        message = self.get_object()
        
        # Only recipient can mark as read
        if message.recipient != request.user:
            return Response(
                {'error': 'Only recipient can mark as read'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.read = True
        message.read_at = timezone.now()
        message.save()
        
        return Response({'message': 'Marked as read'})

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get list of users you have conversations with"""
        user = request.user
        
        # Get unique users from sent and received messages
        sent_to = DirectMessage.objects.filter(
            sender=user
        ).values_list('recipient', flat=True).distinct()
        
        received_from = DirectMessage.objects.filter(
            recipient=user
        ).values_list('sender', flat=True).distinct()
        
        user_ids = set(list(sent_to) + list(received_from))
        
        from accounts.serializers import UserSerializer
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.filter(id__in=user_ids)
        serializer = UserSerializer(users, many=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages"""
        count = DirectMessage.objects.filter(
            recipient=request.user,
            read=False
        ).count()
        
        return Response({'unread_count': count})


class AttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for file attachments"""
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attachment.objects.filter(
            uploaded_by=self.request.user
        )

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        
        if not file:
            raise ValueError("No file provided")
        
        serializer.save(
            uploaded_by=self.request.user,
            filename=file.name,
            file_type=file.content_type,
            file_size=file.size
        )