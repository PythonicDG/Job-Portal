from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from mainapp.models import ExpiringToken

class ExpiringTokenAuthentication(TokenAuthentication):
    model = ExpiringToken
    
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key = key)
        
        except self.model.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")
        
        if not token.user.is_active:
            raise AuthenticationFailed("Invalid Token")
        
        if token.is_expired:
            raise AuthenticationFailed("Token Expired")
        
        return (token.user, token)

