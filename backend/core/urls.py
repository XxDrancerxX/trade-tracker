
"""
URL configuration for core project.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from django.contrib.auth import get_user_model

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .auth_cookies import (
    clear_access_cookie,
    clear_refresh_cookie,
    set_access_cookie,
    set_refresh_cookie,
)
from api.views import SpotTradeViewSet, FuturesTradeViewSet


User = get_user_model()


# ---------- /api/me/ -------------------------------------------------
class MeSerializer(serializers.ModelSerializer):
    """
    Minimal representation of the current user.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/me/
    Returns current authenticated user using CookieJWTAuthentication.
    """
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


# ---------- Auth endpoints (cookie-based) ----------------------------
class CookieTokenObtainPairView(TokenObtainPairView):
    """
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


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh: reads refresh token from cookie if not in body,
    then sets a new HttpOnly access cookie (and refresh if rotation enabled).
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if "refresh" not in request.data:
            cookie_refresh = request.COOKIES.get("tt_refresh")
            if cookie_refresh:
                try:
                    data = request.data.copy()
                except Exception:
                    data = dict(request.data)
                data["refresh"] = cookie_refresh
                # DRF caches parsed data on _full_data
                request._full_data = data

        resp = super().post(request, *args, **kwargs)
        data = resp.data

        out = Response({"ok": True}, status=resp.status_code)

        access = data.get("access")
        if access:
            set_access_cookie(out, access)

        if "refresh" in data:
            set_refresh_cookie(out, data["refresh"])

        return out


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(_request):
    """
    Logout: clears both access and refresh cookies.
    """
    out = Response({"ok": True}, status=status.HTTP_200_OK)
    clear_access_cookie(out)
    clear_refresh_cookie(out)
    return out


# ---------- Routers / misc endpoints --------------------------------
router = DefaultRouter()
router.register(r"spot-trades", SpotTradeViewSet, basename="spottrade")
router.register(r"futures-trades", FuturesTradeViewSet, basename="futurestrade")


def health(_request):
    return JsonResponse(
        {"status": "ok", "service": "trade-tracker-backend", "version": "0.0.1"}
    )


def home(_request):
    return JsonResponse({"message": "✅ Welcome to the Trade Tracker API!"})


urlpatterns = [
    path("", home),
    path("api/health", health),

    # Auth endpoints
    path("api/auth/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/auth/token/refresh/",
        CookieTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("api/auth/logout/", logout_view, name="logout"),

    # Current user
    path("api/me/", me_view, name="me"),

    # Admin + API router
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]