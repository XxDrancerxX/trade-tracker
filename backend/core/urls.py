"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import JsonResponse # to return JSON responses in our views.
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .auth_cookies import set_refresh_cookie, clear_refresh_cookie #> These functions help manage refresh tokens in HttpOnly cookies.
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from api.views import SpotTradeViewSet, FuturesTradeViewSet
from rest_framework import status
from rest_framework.response import Response #> This is used to create HTTP responses in our views.
from rest_framework_simplejwt.views import (
    TokenObtainPairView, #> This view provides an endpoint to obtain a new pair of access and refresh tokens.
    TokenRefreshView, #> This view provides an endpoint to refresh an access token using a valid refresh token.
)
class CookieTokenObtainPairView(TokenObtainPairView):
    """
    POST body: {"username","password"}
    Returns: {"access": "..."}  and sets HttpOnly refresh cookie.
    """
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)   # has access+refresh in body
        data = resp.data
        access = data.get("access")
        refresh = data.get("refresh")
        out = Response({"access": access}, status=resp.status_code)
        if refresh:
            set_refresh_cookie(out, refresh)
        return out

class CookieTokenRefreshView(TokenRefreshView):
    """
    Uses refresh from cookie if body missing.
    Returns: {"access": "..."} and rotates cookie if configured.
    """
    def post(self, request, *args, **kwargs):
        if "refresh" not in request.data:
            cookie_refresh = request.COOKIES.get("tt_refresh")
            if cookie_refresh:
                # Make a mutable copy of the incoming data
                try:
                    data = request.data.copy()
                except Exception:
                    data = dict(request.data)
                data["refresh"] = cookie_refresh
                # DRF uses _full_data internally for .data; overriding is safer than poking at _mutable
                request._full_data = data

        resp = super().post(request, *args, **kwargs)  # SimpleJWT handles validation
        data = resp.data

        out = Response({"access": data.get("access")}, status=resp.status_code)
        if "refresh" in data:
            set_refresh_cookie(out, data["refresh"])
        return out
 
@api_view(["POST"]) #> This decorator specifies that this view only accepts POST requests.
@permission_classes([AllowAny]) #> This decorator allows any user (authenticated or not) to access this view.
def logout_view(_request): #> This view handles user logout by clearing the refresh token cookie.
    out = Response({"ok": True}, status=status.HTTP_200_OK)
    clear_refresh_cookie(out)
    return out    
    
router = DefaultRouter() # => This router automatically generates URL patterns for our viewsets. We register our viewsets with specific URL prefixes.
router.register(r'spot-trades', SpotTradeViewSet, basename='spottrade' ) # => This line registers the SpotTradeViewSet with the router. The URL prefix 'spot-trades' means that all endpoints for this viewset will be accessible under /api/spot-trades/. The basename is used to name the URL patterns.
router.register(r'futures-trades', FuturesTradeViewSet, basename='futurestrade') # => This line registers the FuturesTradeViewSet with the router. The URL prefix 'futures-trades' means that all endpoints for this viewset will be accessible under /api/futures-trades/. The basename is used to name the URL patterns.

def health(_request):
    return JsonResponse({"status": "ok", "service": "trade-tracker-backend", "version": "0.0.1"})

def home(_request):
    return JsonResponse({"message": "✅ Welcome to the Trade Tracker API!"})

urlpatterns = [
    path("", home),
    path("api/health", health),  # ✅ Health check endpoint

    # 🔐 SimpleJWT endpoints    
    path("api/auth/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"), # Obtain access token and set refresh cookie
    path("api/auth/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"), # Refresh access token using refresh cookie
    path("api/auth/logout/", logout_view, name="logout"), # Logout and clear refresh cookie

    path("admin/", admin.site.urls),      # ✅ Keeps the admin panel!     
    path("api/", include(router.urls)),   # ✅ REST API at /api/... # 📦 Our DRF viewsets
]