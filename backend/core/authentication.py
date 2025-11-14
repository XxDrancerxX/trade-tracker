from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads JWT access token from HttpOnly cookie "tt_access".
    If present and valid, authenticates the user.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("tt_access")
        if not raw_token:
            return None  # no cookie → let other authenticators or IsAuthenticated handle it

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception:
            # Token invalid/expired → treat as unauthenticated
            raise AuthenticationFailed("Invalid or expired token")

        user = self.get_user(validated_token)
        return (user, validated_token)
