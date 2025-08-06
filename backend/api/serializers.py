from rest_framework import serializers  
from .models import SpotTrade, FuturesTrade
from django.utils.timezone import localtime
from datetime import timezone

#Defining a serializers for Our .Models using Django REST Framework (DRF):
#First model
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

    #---------------------------------------------------------------------------------------------------
    # SerializerMethodField creates a read-only field in the serializer, not in the model.
    # DRF uses the variable name (e.g., 'trade_time_utc') to find a method called 'get_trade_time_utc'.
    # The return value of that method is inserted into the serialized output under that field name.
    # These fields are not saved in the database — they exist only during serialization (output).
    #  ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
    def get_trade_time_utc(self, obj):
     return obj.trade_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def get_trade_time_local(self, obj):
        return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S") #Converts the UTC time from the database into our server’s local time zone, as set in settings.py


    def to_internal_value(self, data):    
        if "side" in data: 
            data["side"] = data["side"].upper()
        return super().to_internal_value(data) 


#Second model
class FuturesTradeSerializer(serializers.ModelSerializer):# => Converts our .model instances to JSON (and vice versa) for API communication
    trade_time_utc = serializers.SerializerMethodField() # We use SerializerMethodField to add custom, read-only fields (not stored in the model or database).
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

    def get_trade_time_utc(self, obj):
     return obj.trade_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def get_trade_time_local(self, obj):
       return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S") #Converts the UTC time from the database into our server’s local time zone, as set in settings.py

    def to_internal_value(self, data):    
        if "side" in data:
            data["side"] = data["side"].upper()
        return super().to_internal_value(data)