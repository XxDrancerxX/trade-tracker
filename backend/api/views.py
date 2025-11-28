# => ||| Here it's where you define what happens when a request hits your endpoint. ||| <= #
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SpotTrade,FuturesTrade
from .serializers import SpotTradeSerializer, FuturesTradeSerializer, RegisterSerializer
from core.auth_cookies import set_access_cookie, set_refresh_cookie
from core.urls import MeSerializer
# Create your views here.

#We already set IsAuthenticated globally in REST_FRAMEWORK(settings.py), so this line is redundant but harmless.
#It just makes the rule obvious at the view level.

#ViewSet classes automatically provide implementations for standard actions like list, create, retrieve, update, and destroy.
#They map HTTP methods to class methods, allowing us to define behavior for each action in one place.
#This keeps our code DRY and organized.

#------------------------------------- User Registration(Signup-View) --------------------------------------------#
@api_view(["POST"]) # Turns the function into an API endpoint that only accepts POST requests.
@permission_classes([AllowAny]) # Overrides global auth settings to allow anyone (even unauthenticated users) to access this view.
def register_view(request):#request is the HTTP request object containing data sent by the client.
    """
    Public endpoint: create a new user account and log them in.

    Request body (JSON):
    {
        "username": "...",
        "password": "..."
    }
    Response (201):
    {
        "ok": true,
        "user": { ... }   # same shape as /api/me/
    }

    plus HttpOnly cookies: tt_access, tt_refresh
    """
    # 1) Validate input with RegisterSerializer
    serializer = RegisterSerializer(data=request.data) # request.data contains the parsed body of the HTTP request (usually JSON).
    serializer.is_valid(raise_exception=True)

    # 2) Create the user (uses create_user -> password hashed)
    user = serializer.save()

    # 3) Create JWT tokens for this user
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # 4) Build response payload
    payload = {
        "ok": True,
        "user": MeSerializer(user).data,# reuse same shape as /api/me/
    }

    # 5) Attach cookies to the response
    resp = Response(payload, status=status.HTTP_201_CREATED)
    set_access_cookie(resp, str(access))
    set_refresh_cookie(resp, str(refresh))

    return resp

#-------------------------------------Trade ViewSets --------------------------------------------#

class SpotTradeViewSet(viewsets.ModelViewSet):# => automatically builds all RESTful endpoints for your model (GET, POST, PUT, DELETE) without you having to define each one manually.
    serializer_class = SpotTradeSerializer # => Specifies which serializer to use for converting model instances to/from JSON.
    permission_classes = [permissions.IsAuthenticated] # => Ensures that only authenticated users can access these endpoints.

    def get_queryset(self): # => This method defines the set of objects that the view will operate on.
        return SpotTrade.objects.filter(user=self.request.user) # => This method customizes the queryset to only include trades belonging to the currently logged-in user. This ensures users can only see and manage their own trades.

class FuturesTradeViewSet(viewsets.ModelViewSet):
    serializer_class = FuturesTradeSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        return FuturesTrade.objects.filter(user=self.request.user)