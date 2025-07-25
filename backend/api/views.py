from django.shortcuts import render
from rest_framework import viewsets
from .models import SpotTrade,FuturesTrade
from .serializers import SpotTradeSerializer, FuturesTradeSerializer

# Create your views here.
class SpotTradeViewSet(viewsets.ModelViewSet):
    queryset = SpotTrade.objects.all()
    serializer_class = SpotTradeSerializer

class FuturesTradeViewSet(viewsets.ModelViewSet):
    queryset = FuturesTrade.objects.all()
    serializer_class = FuturesTradeSerializer    

