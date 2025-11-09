from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db import models
from django.core.cache import cache
from utils.throttling import RegistrationRateThrottle
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see other users in their workspaces
        user = self.request.user
        return User.objects.filter(
            workspaces__in=user.workspaces.all()
        ).distinct()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        # Try to get from cache first
        cache_key = f"user_profile:{request.user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        serializer = self.get_serializer(request.user)
        # Cache for 5 minutes
        cache.set(cache_key, serializer.data, 300)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Invalidate cache
        cache_key = f"user_profile:{request.user.id}"
        cache.delete(cache_key)
        
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'message': 'Password changed successfully'
        })

    @action(detail=False, methods=['post'])
    def update_status(self, request):
        """Update user online status"""
        status_value = request.data.get('status')
        if status_value not in ['online', 'away', 'busy', 'offline']:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.status = status_value
        request.user.save()
        
        # Update cache
        cache_key = f"user_profile:{request.user.id}"
        cache.delete(cache_key)
        
        # Store online status in Redis with TTL
        online_key = f"user_online:{request.user.id}"
        cache.set(online_key, status_value, 300)  # 5 min TTL
        
        return Response({
            'status': status_value,
            'message': 'Status updated successfully'
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by username or email"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({
                'error': 'Query must be at least 2 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        users = self.get_queryset().filter(
            models.Q(username__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query)
        )
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)