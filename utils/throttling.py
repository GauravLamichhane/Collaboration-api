"""
Create this file: utils/throttling.py
Rate limiting using Redis
"""

from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache


class UserRateThrottle(SimpleRateThrottle):
    """
    Rate limit per user
    100 requests per hour for authenticated users
    """
    scope = 'user'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class AnonRateThrottle(SimpleRateThrottle):
    """
    Rate limit for anonymous users
    20 requests per hour
    """
    scope = 'anon'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class MessageRateThrottle(SimpleRateThrottle):
    """
    Rate limit for sending messages
    60 messages per minute
    """
    scope = 'messages'
    rate = '60/min'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class RegistrationRateThrottle(SimpleRateThrottle):
    """
    Rate limit for registration
    5 registrations per hour per IP
    """
    scope = 'registration'
    rate = '5/hour'
    
    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }