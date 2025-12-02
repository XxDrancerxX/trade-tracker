
"""
URL configuration for core project.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from api.views import register_view  


from rest_framework import  status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from api.serializers import MeSerializer

from .auth_cookies import (
    clear_access_cookie,
    clear_refresh_cookie,
    set_access_cookie,
    set_refresh_cookie,
)
from api.views import SpotTradeViewSet, FuturesTradeViewSet

def health(_request):
    return JsonResponse(
        {"status": "ok", "service": "trade-tracker-backend", "version": "0.0.1"}
    )


def home(_request):
    return JsonResponse({"message": "✅ Welcome to the Trade Tracker API!"})






#View to handle GET requests to /api/me/ and return the current authenticated user's info.
# This is just a auth/me endpoint different from the viewsets defined in api/views.py since they use ModelViewSet for CRUD operations on trade models.
# That's why their URLs are handled different by using DefaultRouter below.
@api_view(["GET"]) # Endpoint only supports GET requests.
@permission_classes([IsAuthenticated]) # Only authenticated users can access this endpoint.
def me_view(request):
    """
    GET /api/me/
    Returns current authenticated user using CookieJWTAuthentication.
    """
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


# ---------- Auth endpoints (cookie-based) ----------------------------
class CookieTokenObtainPairView(TokenObtainPairView): #TokenObtainPairView is a built-in view from SimpleJWT that handles obtaining JWT tokens.
    """
    TokenObtainPairView uses simpleJWT's built=in serializer to validate username/password and return access + refresh tokens.
    Login: validates username/password, then sets HttpOnly access + refresh cookies.
    Response body is just { "ok": true }.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)  # SimpleJWT: access + refresh
        data = resp.data
        access = data.get("access")
        refresh = data.get("refresh")

        out = Response({"ok": True}, status=resp.status_code)
        if access:
            set_access_cookie(out, access)
        if refresh:
            set_refresh_cookie(out, refresh)
        return out


class CookieTokenRefreshView(TokenViewBase):# token refresh view that reads refresh token from cookie if not provided in request body.
    """
    Refresh: uses refresh token from JSON body or tt_refresh cookie.
    - If successful: sets new tt_access (and tt_refresh if rotation is enabled).
    - If it fails: clears cookies and returns 401 with error details.

    """
    serializer_class = TokenRefreshSerializer ## SimpleJWT's built-in serializer for validating refresh tokens and issuing new access tokens.
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.copy() # Make a mutable copy of request data.
        refresh = data.get("refresh")  or request.COOKIES.get("tt_refresh") # Try to get refresh token from request body first, then from cookie.
        
        if not refresh: # If no refresh token is found, return 401 Unauthorized.
            resp = Response(
                {"detail": "Refresh token not provided."},
                status = status.HTTP_401_UNAUTHORIZED
            )
            clear_access_cookie(resp) # Clear any existing access/refresh cookies.
            clear_refresh_cookie(resp)  # Clear any existing access/refresh cookies.
            return resp    
        
        serializer = self.get_serializer(data={"refresh": refresh}) # Initialize serializer with the refresh token.

        try:
            serializer.is_valid(raise_exception=True) # Validate the refresh token.
        except Exception :
             # Invalid/expired refresh → clear cookies & return errors
            resp = Response( # Return 401 Unauthorized with error details.
                serializer.errors,
                status=status.HTTP_401_UNAUTHORIZED
            )
            clear_access_cookie(resp)
            clear_refresh_cookie(resp)
            return resp
        
        # Valid refresh → set new cookies
        validated = serializer.validated_data # Get validated data from serializer.
        access = validated.get("access")
        new_refresh = validated.get("refresh", refresh) # Get new refresh token if rotation is enabled.

        resp = Response({"ok": True}, status=status.HTTP_200_OK) # Create response with success message.

        if access:
            set_access_cookie(resp, access) # Set new access token cookie.
        if new_refresh:
            set_refresh_cookie(resp, new_refresh)

        return resp    

     
        

        
# Token endpoints rely on SimpleJWT’s built-in serializers (they validate credentials against the existing User model). Tokens aren’t saved to the database, so no token model is needed.
# The only “persistence” is the JWT cookies; the payload carries user ID/exp, and verification uses your SECRET_KEY + SimpleJWT settings.

#===--------- Logout endpoint --------------------------------------------------
# Logout view that clears both access and refresh cookies.
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(_request): #_request is  a placeholder for the request parameter that is not used in the function.
    """
    Logout: clears both access and refresh cookies.
    """
    out = Response({"ok": True}, status=status.HTTP_200_OK)
    clear_access_cookie(out) #clear_access_cookie and clear_refresh_cookie are utility functions that remove the respective cookies from the response.
    clear_refresh_cookie(out)
    return out


# ---------- Routers / misc endpoints --------------------------------
## 
router = DefaultRouter() # => DefaultRouter automatically creates URL routes for our viewsets, following RESTful conventions(list/create/detail).
router.register(r"spot-trades", SpotTradeViewSet, basename="spottrade")
router.register(r"futures-trades", FuturesTradeViewSet, basename="futurestrade")




urlpatterns = [
    path("", home),
    path("api/health", health),

    # Auth endpoints
    path("api/auth/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),        
    path("api/auth/logout/", logout_view, name="logout"),
    path("api/auth/register/", register_view, name="register"),

    # Current user
    path("api/me/", me_view, name="me"),

    # Admin + API router
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)), # => Includes all the automatically generated routes for our API endpoints (spot-trades, futures-trades).
]
