from rest_framework import serializers  
from .models import SpotTrade, FuturesTrade

class SpotTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotTrade
        fields = "__all__"

class FuturesTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuturesTrade
        fields = "__all__"        