from rest_framework import serializers  
from .models import SpotTrade, FuturesTrade
from django.utils.timezone import localtime
from datetime import timezone

#Defining a serializers for Our .Models using Django REST Framework (DRF):

class SpotTradeSerializer(serializers.ModelSerializer): # => Converts our .model instances to JSON (and vice versa) for API communication

    trade_time_utc = serializers.SerializerMethodField()  #This field will be calculated using a custom method you define.We use SerializerMethodField to add custom, read-only fields (not stored in the model or database).
    trade_time_local = serializers.SerializerMethodField()

    class Meta: #Meta is a special inner class sed to configure behavior for other classes like ModelSerializer.
        model = SpotTrade
        fields = [
            'id', 'symbol', 'price', 'amount', 'side',
            'exchange', 'currency', 'notes', 'user',
            'trade_time_utc', 'trade_time_local'  # =>We add our customs-fields made above  provided by SerializerMethodField.
        ]
        read_only_fields = ('trade_time',) # =>This field should only be included in the output,So clients can see it, but can’t send or change it.Django sets this field automatically when the object is saved in our .Models.

    def get_trade_time_utc(self, obj):
     return obj.trade_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def get_trade_time_local(self, obj):
        return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S")


    def to_internal_value(self, data):    
        if "side" in data: 
            data["side"] = data["side"].upper()
        return super().to_internal_value(data)

 



class FuturesTradeSerializer(serializers.ModelSerializer):# => Converts our .model instances to JSON (and vice versa) for API communication
    trade_time_utc = serializers.DateTimeField(source='trade_time', read_only=True) # We use SerializerMethodField to add custom, read-only fields (not stored in the model or database).
    trade_time_local = serializers.SerializerMethodField()

    class Meta:#Meta is a special inner class sed to configure behavior for other classes like ModelSerializer.
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
