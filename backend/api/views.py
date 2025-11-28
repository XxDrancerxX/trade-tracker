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
from api.serializers import MeSerializer
# Create your views here.

#We already set IsAuthenticated globally in REST_FRAMEWORK(settings.py), so this line is redundant but harmless.
#It just makes the rule obvious at the view level.

#ViewSet classes automatically provide implementations for standard actions like list, create, retrieve, update, and destroy.
#They map HTTP methods to class methods, allowing us to define behavior for each action in one place.
#This keeps our code DRY and organized.

#------------------------------------- User Registration(Signup-View) --------------------------------------------#
@api_view(["POST"]) # Turns the function into an API endpoint that only accepts POST requests.
@permission_classes([AllowAny]) # Overrides global auth settings to allow anyone (even unauthenticated users) to access this view.
def register_view(request):#request is a parameter that represents the HTTP request object containing data sent by the client.
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
    #We pass the request as : data=request.data  to construct a serializer in “write/deserialization” mode so it can validate and save new data.
    #Passing request.data without the data= keyword   would be treated as the instance positional argument, which is for “read/serialization” mode.
    #so validation wouldn’t run and the serializer would behave incorrectly.
    
    serializer = RegisterSerializer(data=request.data) # request.data contains the parsed body of the HTTP request (usually JSON).
    serializer.is_valid(raise_exception=True) # It triggers the whole validation pipeline we configured on RegisterSerializer plus any default Django validators (max length, required fields)
    # If not, it raises an error and returns a 400 Bad Request response.

    # 2) Create the user (uses create_user -> password hashed)
    user = serializer.save() # If validation passes, we call save() on the serializer to create and persist the new User instance in the database 
    # Using create_user which hashes the password and writes the row to the database. The return value is the newly created User instance, assigned to user.

    # 3) Create JWT tokens for this user
    #RefreshToken is a class from djangorestframework-simplejwt.tokens.py that helps create and manage JWT refresh tokens.
    #Builds the JWT payload {"token_type": "refresh", "user_id": <id>, "exp": <expiry>, ...}) using settings like AUTH_USER_MODEL primary key field.
    # Signs it with the SECRET_KEY to produce the final encoded token string.
    #Returns a RefreshToken object that represents the refresh token for the given user and whose string form str(refresh)) is the compact JWT (header.payload.signature).
    #for_user is a class method of RefreshToken that builds a brand-new refresh token for that user instance.
    #It copies user info into the token payload and signs it.
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    # Access token is a property defined on SimpleJWT’s RefreshToken class that derives a new access token from the refresh token.
    # It creates a new JWT with a shorter expiry that can be used to authenticate API requests

    # 4) Build response payload
    #This blocks constructs the JSON response body that will be sent back to the client or returned to the frontend.
    payload = {
        "ok": True,
        "user": MeSerializer(user).data,# reuse same shape as /api/me/
        #runs the new user through MeSerializer to convert it to a JSON-serializable format.
        #This serializer inspects the User instance, pulls fields like id/username/email, and converts them into plain Python data. Accessing .data returns those values ready to be rendered as JSON.
        #.data property of the serializer gives us the serialized representation of the user instance:
    # class Serializer:
    # @property
    # def data(self):
    #     return self.to_representation(...)
    }


    # 5) Attach cookies to the response
    resp = Response(payload, status=status.HTTP_201_CREATED) # Create the DRF Response object with our payload and a 201 Created status code.
    set_access_cookie(resp, str(access)) # Set the HttpOnly access token cookie on the response.
    set_refresh_cookie(resp, str(refresh)) # Set the HttpOnly refresh token cookie on the response.

    return resp # Return the response to the client, completing the registration process.

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