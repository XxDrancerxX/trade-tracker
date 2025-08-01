# => ||| Here it's where you define what happens when a request hits your endpoint. ||| <= #
from django.shortcuts import render
from rest_framework import viewsets
from .models import SpotTrade,FuturesTrade
from .serializers import SpotTradeSerializer, FuturesTradeSerializer

# Create your views here.
class SpotTradeViewSet(viewsets.ModelViewSet): # => automatically builds all RESTful endpoints for your model (GET, POST, PUT, DELETE) without you having to define each one manually.
    queryset = SpotTrade.objects.all() # =>It's the default data pulled from our .Models, queryset is the special built-in atttribute of Django Rest. We must use this exact name to  use our.Models.
    serializer_class = SpotTradeSerializer

class FuturesTradeViewSet(viewsets.ModelViewSet):# => automatically builds all RESTful endpoints for your model (GET, POST, PUT, DELETE) without you having to define each one manually.
    queryset = FuturesTrade.objects.all()# => It's the default data pulled from our .Models, queryset is the special built-in atttribute of Django Rest. We must use this exact name to  use our.Models.
    serializer_class = FuturesTradeSerializer # => This is the serializer to use when converting data between JSON and Python objects.

