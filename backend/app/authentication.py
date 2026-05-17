from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        
        token = request.COOKIES.get('access_token')

        if not token:
            auth = get_authorization_header(request).split()
            if auth and len(auth) == 2:
                
                token = auth[1].decode() if isinstance(auth[1], bytes) else auth[1]

        if not token:
            return None

        try:
            access_token = AccessToken(token)

            user_id = access_token.get('user_id')
            if not user_id:
                return None

            User = get_user_model()
            user = User.objects.get(id=user_id)
            return (user, None)
        except Exception:
            return None