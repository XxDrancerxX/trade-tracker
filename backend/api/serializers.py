from rest_framework import serializers  # => DRF serializers module provides tools to convert complex data types, such as Django model instances, 
# into native Python datatypes that can then be easily rendered into JSON, XML, or other content types. It also provides deserialization,
# allowing parsed data to be converted back into complex types, after first validating the incoming data.
from .models import SpotTrade, FuturesTrade, ExchangeCredential # Bring in the Django model classes that the serializers serialize/deserialize.
from django.utils.timezone import localtime #Django utility to convert UTC times to local time zone.
from datetime import timezone #Python standard library module for working with dates and times, including time zones.
from .services.crypto_vault import CryptoVault

##////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#These serializers handle the conversion between our Django models and JSON representations for API communication.
##////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

## ===>>>⚡ Notice: You don’t send user, id, or trade_time → they are filled automatically.(Post method) <<<==== ##
#Django REST Framework (DRF) serializer. (Django REST Framework.)
# It’s designed to validate and transform input data (usually from an API request) into a model instance.

#Defining a serializers for Our .Models using Django REST Framework (DRF):
#First model
class SpotTradeSerializer(serializers.ModelSerializer): # => Converts our .model instances to JSON (and vice versa) for API communication
    # Auto-attach the logged-in user; hidden from requests/responses by default.
    #During deserialization (POST/PUT), DRF auto-fills user with request.user.
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # => You don’t include user in POST bodies.Automatically sets the user field to the currently authenticated user making the request.
    #This way, clients don’t have to (and can’t) specify the user when creating or updating a trade; it’s handled by the server.
    # HiddenField is used for fields that should not be exposed to the API consumer.It’s not shown in output and not expected in input.
    #serializers.CurrentUserDefault() is a DRF utility that retrieves the currently authenticated user from the request context.
    trade_time_utc = serializers.SerializerMethodField()  #This field will be calculated using a custom method you define.We use SerializerMethodField to add custom, read-only fields (not stored in the model or database).
    trade_time_local = serializers.SerializerMethodField() 

    class Meta: #Meta is a special inner class sed to configure behavior for other classes like ModelSerializer.
        model = SpotTrade
        fields = [ #List of fields to include in the serialized output and expected in input.
            'id', 'symbol', 'price', 'amount', 'side',
            'exchange', 'currency', 'notes', 'user',
            'trade_time_utc', 'trade_time_local','trade_time'  # =>We add our customs-fields made above  provided by SerializerMethodField.
        ]
        read_only_fields = ('trade_time','id') # =>This field should only be included in the output,So clients can see it, but can’t send or change it.Django sets this field automatically when the object is saved in our .Models.

    #---------------------------------------------------------------------------------------------------------------------------------------
    # SerializerMethodField creates a read-only field in the serializer, not in the model.
    # DRF uses the variable name (e.g., 'trade_time_utc') to find a method called 'get_trade_time_utc'.
    # The return value of that method is inserted into the serialized output under that field name.
    # These fields are not saved in the database — they exist only during serialization (output).
    #  ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
    def get_trade_time_utc(self, obj):
     return obj.trade_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") #Converts the trade_time to UTC and formats it as a string.

    def get_trade_time_local(self, obj):
        return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S") #Converts the UTC time with "localtime()" from the database into our server’s local time zone, as set in settings.py


    def to_internal_value(self, data):
        if "side" in data and isinstance(data["side"], str): # => This method is called during deserialization, when converting incoming data (e.g., from a POST request) into a model instance. Here, we ensure that the 'side' field is always stored in uppercase.
            data["side"] = data["side"].upper()
        return super().to_internal_value(data) 

#===============================================================================================================================

#Second model
class FuturesTradeSerializer(serializers.ModelSerializer):# => Converts our .model instances to JSON (and vice versa) for API communication
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # => Automatically sets the user field to the currently authenticated user making the request. This way, clients don’t have to (and can’t) specify the user when creating or updating a trade; it’s handled by the server.
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
            'trade_time_local',
            'trade_time'
        ]
        read_only_fields = ('trade_time','id') # =>This field should only be included in the output,So clients can see it, but can’t send or change it.Django sets this field automatically when the object is saved in our .Models.

    def get_trade_time_utc(self, obj):
     return obj.trade_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def get_trade_time_local(self, obj):
       return localtime(obj.trade_time).strftime("%Y-%m-%d %H:%M:%S") #Converts the UTC time from the database into our server’s local time zone, as set in settings.py

    def to_internal_value(self, data):
        if "side" in data and isinstance(data["side"], str): # => This method is called during deserialization, when converting incoming data (e.g., from a POST request) into a model instance. Here, we ensure that the 'side' field is always stored in uppercase.
            data["side"] = data["side"].upper()
        return super().to_internal_value(data)

#===============================================================================================================================

#Third model
class ExchangeCredentialCreateSerializer(serializers.ModelSerializer):#ModelSerializer auto-generates fields for model fields in Meta.fields (exchange, label, can_trade, can_transfer).
    # three extra fields added for input only (write_only=True) - not stored directly in the model
    # These are the “explicitly declared fields.”
    """
    Accepts plaintext once at the boundary, encrypts immediately with CryptoVault,
    saves to *_enc. Attaches the row to request.user. Never returns plaintext.
    """

    api_key = serializers.CharField(write_only=True)
    api_secret = serializers.CharField(write_only=True)
    passphrase = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = ExchangeCredential
        fields = ["exchange", "label", "api_key", "api_secret", "passphrase", "can_trade", "can_transfer"]

    def create(self, validated):
        v = CryptoVault()
        return ExchangeCredential.objects.create(
            user=self.context["request"].user,
            exchange=validated["exchange"],
            label=validated.get("label","default"),
            api_key_enc=v.enc(validated["api_key"]),
            api_secret_enc=v.enc(validated["api_secret"]),
            passphrase_enc=v.enc(validated.get("passphrase","")) if validated.get("passphrase") else None,
            can_trade=validated.get("can_trade", True),
            can_transfer=validated.get("can_transfer", False),
        )