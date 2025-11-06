from rest_framework import serializers
from .models import Workspace, WorkspaceMember, Channel, ChannelMember
from accounts.serializers import UserSerializer


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """Serializer for workspace members"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for workspace"""
    
    owner = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    channel_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'description', 'owner',
            'member_count', 'channel_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_channel_count(self, obj):
        return obj.channels.count()
    
    def create(self, validated_data):
        user = self.context['request'].user
        workspace = Workspace.objects.create(owner=user, **validated_data)
        # Automatically add owner as admin member
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role='owner'
        )
        return workspace


class WorkspaceDetailSerializer(WorkspaceSerializer):
    """Detailed workspace serializer with members"""
    
    members_list = WorkspaceMemberSerializer(
        source='workspacemember_set',
        many=True,
        read_only=True
    )
    
    class Meta(WorkspaceSerializer.Meta):
        fields = WorkspaceSerializer.Meta.fields + ['members_list']


class ChannelMemberSerializer(serializers.ModelSerializer):
    """Serializer for channel members"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChannelMember
        fields = ['id', 'user', 'joined_at', 'last_read_at']
        read_only_fields = ['id', 'joined_at']


class ChannelSerializer(serializers.ModelSerializer):
    """Serializer for channels"""
    
    created_by = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Channel
        fields = [
            'id', 'workspace', 'name', 'slug', 'description',
            'channel_type', 'created_by', 'member_count', 'is_member',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False
    
    def create(self, validated_data):
        user = self.context['request'].user
        channel = Channel.objects.create(created_by=user, **validated_data)
        # Automatically add creator as member
        ChannelMember.objects.create(channel=channel, user=user)
        return channel


class ChannelDetailSerializer(ChannelSerializer):
    """Detailed channel serializer with members"""
    
    members_list = ChannelMemberSerializer(
        source='channelmember_set',
        many=True,
        read_only=True
    )
    
    class Meta(ChannelSerializer.Meta):
        fields = ChannelSerializer.Meta.fields + ['members_list']