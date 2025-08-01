from rest_framework import serializers  
from .models import SpotTrade, FuturesTrade
from django.utils.timezone import localtime
from datetime import timezone


class SpotTradeSerializer(serializers.ModelSerializer):
    trade_time_utc = serializers.SerializerMethodField()
    trade_time_local = serializers.SerializerMethodField()

    class Meta:
        model = SpotTrade
        fields = [
            'id', 'symbol', 'price', 'amount', 'side',
            'exchange', 'currency', 'notes', 'user',
            'trade_time_utc', 'trade_time_local'  
        ]
        read_only_fields = ('trade_time',)

    def get_trade_time_utc(self, obj):
     return obj.trade_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def get_trade_time_local(self, obj):
        return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S")


    def to_internal_value(self, data):    
        if "side" in data: 
            data["side"] = data["side"].upper()
        return super().to_internal_value(data)

 



class FuturesTradeSerializer(serializers.ModelSerializer):
    trade_time_utc = serializers.DateTimeField(source='trade_time', read_only=True)
    trade_time_local = serializers.SerializerMethodField()

    class Meta:
        model = FuturesTrade
        fields = [
            'id',
            'symbol',
            'price',
            'entry_price',
            'liquidation_price',
            'leverage',
            'pnl',
            'exchange',
            'amount',
            'side',
            'currency',
            'notes',
            'user',
            'trade_time_utc',
            'trade_time_local'
        ]
        read_only_fields = ("trade_time",)

    def to_internal_value(self, data):    
        if "side" in data:
            data["side"] = data["side"].upper()
        return super().to_internal_value(data)

    def get_trade_time_local(self, obj):
        # Convert to server-local time (as defined in settings.py)
        return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S")
