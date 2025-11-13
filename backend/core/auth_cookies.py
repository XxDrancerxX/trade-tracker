# core/auth_cookies.py
from django.conf import settings # To access Django settings

REFRESH_COOKIE_NAME = "tt_refresh"

def set_refresh_cookie(response, refresh_token): # Sets the refresh token in an HttpOnly cookie
    response.set_cookie(
        REFRESH_COOKIE_NAME, # Name of the cookie
        refresh_token, # Value of the cookie
        max_age=7*24*3600,         # match refresh lifetime
        httponly=True,
        secure=not settings.DEBUG, # True in prod
        samesite="Lax",
        path="/",                  # or a narrower path if you prefer
    )

def clear_refresh_cookie(response):
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")

