# => ||| Here it's where you define what happens when a request hits your endpoint. ||| <= #
from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import SpotTrade,FuturesTrade
from .serializers import SpotTradeSerializer, FuturesTradeSerializer
# Create your views here.

#We already set IsAuthenticated globally in REST_FRAMEWORK(settings.py), so this line is redundant but harmless.
#It just makes the rule obvious at the view level.

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