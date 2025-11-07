from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, DirectMessageViewSet, AttachmentViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'direct-messages', DirectMessageViewSet, basename='direct-message')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]