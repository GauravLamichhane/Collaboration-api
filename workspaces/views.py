from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Workspace, WorkspaceMember, Channel, ChannelMember
from .serializers import (
    WorkspaceSerializer,
    WorkspaceDetailSerializer,
    WorkspaceMemberSerializer,
    ChannelSerializer,
    ChannelDetailSerializer,
    ChannelMemberSerializer
)
from .permissions import IsWorkspaceOwnerOrAdmin, IsWorkspaceMember


class WorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for workspace operations"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WorkspaceDetailSerializer
        return WorkspaceSerializer

    def get_queryset(self):
        # Return workspaces where user is a member
        return Workspace.objects.filter(
            members=self.request.user
        ).distinct()

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to workspace"""
        workspace = self.get_object()
        
        # Check if requester is owner or admin
        membership = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=['owner', 'admin']
        ).first()
        
        if not membership:
            return Response(
                {'error': 'Only owners and admins can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already a member
        if WorkspaceMember.objects.filter(
            workspace=workspace,
            user_id=user_id
        ).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member = WorkspaceMember.objects.create(
            workspace=workspace,
            user_id=user_id,
            role=role
        )
        
        serializer = WorkspaceMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a member from workspace"""
        workspace = self.get_object()
        
        # Check if requester is owner or admin
        membership = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=['owner', 'admin']
        ).first()
        
        if not membership:
            return Response(
                {'error': 'Only owners and admins can remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        member = get_object_or_404(
            WorkspaceMember,
            workspace=workspace,
            user_id=user_id
        )
        
        # Can't remove the owner
        if member.role == 'owner':
            return Response(
                {'error': 'Cannot remove workspace owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def update_member_role(self, request, pk=None):
        """Update member role"""
        workspace = self.get_object()
        
        # Only owner can change roles
        if workspace.owner != request.user:
            return Response(
                {'error': 'Only workspace owner can change roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        member = get_object_or_404(
            WorkspaceMember,
            workspace=workspace,
            user_id=user_id
        )
        
        member.role = new_role
        member.save()
        
        serializer = WorkspaceMemberSerializer(member)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all workspace members"""
        workspace = self.get_object()
        members = WorkspaceMember.objects.filter(workspace=workspace)
        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)


class ChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for channel operations"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChannelDetailSerializer
        return ChannelSerializer

    def get_queryset(self):
        workspace_id = self.request.query_params.get('workspace')
        
        # Get channels where user is a member
        queryset = Channel.objects.filter(
            members=self.request.user
        )
        
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        return queryset.distinct()

    def perform_create(self, serializer):
        channel = serializer.save()
        # Auto-add all workspace members to public channels
        if channel.channel_type == 'public':
            workspace_members = channel.workspace.members.all()
            for member in workspace_members:
                ChannelMember.objects.get_or_create(
                    channel=channel,
                    user=member
                )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a channel"""
        channel = self.get_object()
        
        # Check if private channel
        if channel.channel_type == 'private':
            return Response(
                {'error': 'Cannot join private channels'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is workspace member
        if not channel.workspace.members.filter(id=request.user.id).exists():
            return Response(
                {'error': 'Must be workspace member to join'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        member, created = ChannelMember.objects.get_or_create(
            channel=channel,
            user=request.user
        )
        
        if created:
            return Response({
                'message': 'Joined channel successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Already a member'
            })

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a channel"""
        channel = self.get_object()
        
        try:
            member = ChannelMember.objects.get(
                channel=channel,
                user=request.user
            )
            member.delete()
            return Response({
                'message': 'Left channel successfully'
            })
        except ChannelMember.DoesNotExist:
            return Response(
                {'error': 'Not a member of this channel'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite user to private channel"""
        channel = self.get_object()
        
        # Check if requester is member
        if not channel.members.filter(id=request.user.id).exists():
            return Response(
                {'error': 'Only members can invite others'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        
        # Check if user is workspace member
        if not channel.workspace.members.filter(id=user_id).exists():
            return Response(
                {'error': 'User must be workspace member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member, created = ChannelMember.objects.get_or_create(
            channel=channel,
            user_id=user_id
        )
        
        if created:
            return Response({
                'message': 'User invited successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'User already a member'
            })