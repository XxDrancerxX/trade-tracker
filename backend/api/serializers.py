from rest_framework import serializers  
from .models import SpotTrade, FuturesTrade

class SpotTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotTrade
        fields = "__all__"

    def to_internal_value(self, data):    
        if "side" in data: 
         data["side"] = data["side"].upper() ##We convert the data in uppercase since we have it as Capital in Models.py
        return super().to_internal_value(data) ### Passes the modified data (with 'side' uppercased) to DRF’s base serializer logic to handle field validation and conversion.

class FuturesTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuturesTrade
        fields = "__all__"        

    def to_internal_value(self, data):    
        if "side" in data:
         data["side"] = data["side"].upper()
        return super().to_internal_value(data)  
