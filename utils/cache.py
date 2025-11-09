from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def generate_cache_key(prefix, *args, **kwargs):
    """Generate a unique cache key"""
    key_data = f"{prefix}:{':'.join(map(str, args))}"
    if kwargs:
        key_data += f":{json.dumps(kwargs, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_user_profile(user_id, timeout=300):
    """Cache decorator for user profile"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            #checks cache first
            cache_key = f"user_profile:{user_id}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data#returns immediately(fast)
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_user_cache(user_id):
    """Invalidate user profile cache"""
    cache_key = f"user_profile:{user_id}"
    cache.delete(cache_key)


def cache_workspace_list(user_id, timeout=300):
    """Cache workspace list for user"""
    cache_key = f"workspace_list:{user_id}"
    cached_data = cache.get(cache_key)
    return cached_data, cache_key


def invalidate_workspace_cache(workspace_id):
    """Invalidate workspace cache"""
    cache.delete_pattern(f"*workspace:{workspace_id}*")
    cache.delete_pattern(f"*workspace_list*")


def cache_channel_messages(channel_id, page=1, timeout=60):
    """Cache channel messages"""
    cache_key = f"channel_messages:{channel_id}:page:{page}"
    cached_data = cache.get(cache_key)
    return cached_data, cache_key


def invalidate_channel_cache(channel_id):
    """Invalidate channel message cache"""
    cache.delete_pattern(f"*channel_messages:{channel_id}*")


class CacheKeys:
    """Centralized cache key definitions"""
    
    @staticmethod
    def user_profile(user_id):
        return f"user_profile:{user_id}"
    
    @staticmethod
    def workspace_list(user_id):
        return f"workspace_list:{user_id}"
    
    @staticmethod
    def workspace_detail(workspace_id):
        return f"workspace_detail:{workspace_id}"
    
    @staticmethod
    def channel_list(workspace_id):
        return f"channel_list:{workspace_id}"
    
    @staticmethod
    def channel_messages(channel_id, page=1):
        return f"channel_messages:{channel_id}:page:{page}"
    
    @staticmethod
    def user_online_status(user_id):
        return f"user_online:{user_id}"
    
    @staticmethod
    def unread_count(user_id):
        return f"unread_count:{user_id}"