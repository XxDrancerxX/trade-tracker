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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response # to create HTTP responses with data.
from rest_framework.routers import DefaultRouter 
from api.views import SpotTradeViewSet, FuturesTradeViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# ---------- Routers for your existing viewsets ---------- #
router = DefaultRouter() # => This router automatically generates URL patterns for our viewsets. We register our viewsets with specific URL prefixes.
router.register(r'spot-trades', SpotTradeViewSet, basename='spottrade' ) # => This line registers the SpotTradeViewSet with the router. The URL prefix 'spot-trades' means that all endpoints for this viewset will be accessible under /api/spot-trades/. The basename is used to name the URL patterns.
router.register(r'futures-trades', FuturesTradeViewSet, basename='futurestrade') # => This line registers the FuturesTradeViewSet with the router. The URL prefix 'futures-trades' means that all endpoints for this viewset will be accessible under /api/futures-trades/. The basename is used to name the URL patterns.

# ---------- Utility views ---------- ---------- #
@api_view(["GET"]) #decorator that that turns a normal Django function view into a DRF function-based API view.Specifies that this view only accepts GET requests.
@permission_classes([AllowAny])# DRF decorator that  sets the permission classes for this view to AllowAny, meaning anyone can access it.
def home_view(_request):
    """
    Simple root endpoint:
    Confirms the API is up and gives a friendly message.
    """
    return Response({"message": "✅ Welcome to the Trade Tracker API!"})


@api_view(["GET"])
@permission_classes([AllowAny])
def health_view(_request):
    """
    Lightweight health check.
    Keep it free of DB / external calls so infra & tests can rely on it.
    """
    return Response(
        {
            "status": "ok",
            "service": "trade-tracker-backend",
            "version": "0.0.1",
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Returns basic info about the authenticated user.
    Frontend will call this after login to hydrate session.
    """
    u = request.user # => Retrieves the currently authenticated user from the request.
    return Response(
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
        }
    )


# ---------- URL patterns ---------- ---------- #
# Why two token endpoints?
# /api/auth/token/ (TokenObtainPairView)
# Accepts credentials (username/password) and returns a token pair: { "access": "<jwt>", "refresh": "<jwt>" }.
# You use this to log in and get tokens.
# /api/auth/token/refresh/ (TokenRefreshView)
# Accepts the refresh token and returns a new access token (and optionally a rotated refresh).
# Purpose: keep access tokens short-lived (safer) while allowing the client to obtain new access tokens without re-sending user credentials.

# TokenObtainPairView (POST /api/auth/token/)
# Use when the user signs in with credentials.

# TokenRefreshView (POST /api/auth/token/refresh/)
# Use when the access token expired (or is about to).

# Access tokens are short-lived for safety. Refresh tokens are longer-lived and used only to get new access tokens. 
# This avoids sending user credentials frequently and limits exposure if an access token is leaked.

# You get a pair of tokens so the client can call APIs (access) and later refresh (refresh) without asking for credentials again.
urlpatterns = [
    path("", home_view, name="home"), # ✅ Root endpoint
    path("health/", health_view, name="health"),  # ✅ Health check endpoint
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"), # ✅ JWT token obtain endpoint
    # TokenObtainPairView is a built-in view from Simple JWT that provides an endpoint for obtaining JWT access and refresh tokens.
    # Internally uses a serializer (TokenObtainPairView) to check username/password and to build the tokens.
    # as_view() converts the class-based(TokenObtainPairSerializer) view into a callable view function.
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), # ✅ JWT token refresh endpoint
    # TokenRefreshView is a built-in view from Simple JWT that provides an endpoint for refreshing JWT access tokens using a valid refresh token.
    # as_view() converts the class-based(TokenRefreshSerializer) view into a callable view function
    path("api/me/", me_view, name="me"), # ✅ Authenticated user info endpoint
    path("admin/", admin.site.urls),      # ✅ Keeps the admin panel! 
    path("api/", include(router.urls)),   # ✅ API routes for spot and futures trades/ REST API at /api/... routes (viewsets)
]


