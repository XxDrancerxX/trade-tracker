# filepath: /workspaces/trade-tracker/backend/core/auth_cookies.py
# This module provides helper functions to set and clear authentication cookiess on Django responses for auth.

from rest_framework_simplejwt.settings import api_settings as jwt_settings # to access JWT settings like token lifetimes.
#api_settings contains settings like ACCESS_TOKEN_LIFETIME and REFRESH_TOKEN_LIFETIME.


def _cookie_params(max_age: int) -> dict:
    """
    Shared cookie flags for auth cookies.

    We hard-code:
    - Secure=True      -> required for SameSite=None in modern browsers
    - SameSite="None"  -> allows cross-origin requests (5173 -> 8000) with credentials
    - path="/"         -> cookie sent to all API paths
    """
    return {
        "max_age": max_age,
        "httponly": True,
        "secure": True,
        "samesite": "None",
        "path": "/",
    }


def set_refresh_cookie(response, refresh_token: str) -> None:
    lifetime = jwt_settings.REFRESH_TOKEN_LIFETIME
    max_age = int(lifetime.total_seconds())
    response.set_cookie("tt_refresh", refresh_token, **_cookie_params(max_age))


def clear_refresh_cookie(response) -> None:
    response.delete_cookie("tt_refresh", path="/")


def set_access_cookie(response, access_token: str) -> None:
    lifetime = jwt_settings.ACCESS_TOKEN_LIFETIME
    max_age = int(lifetime.total_seconds())
    response.set_cookie("tt_access", access_token, **_cookie_params(max_age))


def clear_access_cookie(response) -> None:
    response.delete_cookie("tt_access", path="/")
