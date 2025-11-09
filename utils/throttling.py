from rest_framework.throttling import SimpleRateThrottle


class UserRateThrottle(SimpleRateThrottle):
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
    scope = 'anon'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class MessageRateThrottle(SimpleRateThrottle):
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
    scope = 'registration'
    rate = '5/hour'
    
    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }