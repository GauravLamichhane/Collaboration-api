from django.core.cache import cache


class CacheKeys:
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