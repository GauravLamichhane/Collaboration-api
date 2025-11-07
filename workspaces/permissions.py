from rest_framework import permissions
from .models import WorkspaceMember


class IsWorkspaceOwner(permissions.BasePermission):
    """Permission to check if user is workspace owner"""
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsWorkspaceOwnerOrAdmin(permissions.BasePermission):
    """Permission to check if user is workspace owner or admin"""
    
    def has_object_permission(self, request, view, obj):
        # For safe methods, just check if member
        if request.method in permissions.SAFE_METHODS:
            return obj.members.filter(id=request.user.id).exists()
        
        # For unsafe methods, check if owner or admin
        membership = WorkspaceMember.objects.filter(
            workspace=obj,
            user=request.user,
            role__in=['owner', 'admin']
        ).first()
        
        return membership is not None


class IsWorkspaceMember(permissions.BasePermission):
    """Permission to check if user is workspace member"""
    
    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id).exists()


class IsChannelMember(permissions.BasePermission):
    """Permission to check if user is channel member"""
    
    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id).exists()


class IsMessageSender(permissions.BasePermission):
    """Permission to check if user is the message sender"""
    
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user