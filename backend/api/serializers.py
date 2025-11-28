from rest_framework import serializers  # => DRF serializers module provides tools to convert complex data types, such as Django model instances, 
# into native Python datatypes that can then be easily rendered into JSON, XML, or other content types. It also provides deserialization,
# allowing parsed data to be converted back into complex types, after first validating the incoming data.
from .models import SpotTrade, FuturesTrade, ExchangeCredential # Bring in the Django model classes that the serializers serialize/deserialize.
from django.utils.timezone import localtime #Django utility to convert UTC times to local time zone.
from datetime import timezone #Python standard library module for working with dates and times, including time zones.
from .services.crypto_vault import CryptoVault
from django.contrib.auth import get_user_model, password_validation



User = get_user_model() #Get the currently active user model, which may be a custom user model.


##////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#These serializers handle the conversion between our Django models and JSON representations for API communication.
##////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

## ===>>>⚡ Notice: You don’t send user, id, or trade_time → they are filled automatically.(Post method) <<<==== ##
#Django REST Framework (DRF) serializer. (Django REST Framework.)
# It’s designed to validate and transform input data (usually from an API request) into a model instance.

#===============================================================================================================================

#Defining a serializers for Our .Models using Django REST Framework (DRF):
#First serializer for SpotTrade model
class SpotTradeSerializer(serializers.ModelSerializer): # => Converts our .model instances to JSON (and vice versa) for API communication
    # Auto-attach the logged-in user; hidden from requests/responses by default.
    #During deserialization (POST/PUT), DRF auto-fills user with request.user.
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) # => You don’t include user in POST bodies.Automatically sets the user field to the currently authenticated user making the request.
    #This way, clients don’t have to (and can’t) specify the user when creating or updating a trade; it’s handled by the server.
    # HiddenField is used for fields that should not be exposed to the API consumer.It’s not shown in output and not expected in input.
    #serializers.CurrentUserDefault() is a DRF utility that retrieves the currently authenticated user from the request context.
    trade_time_utc = serializers.SerializerMethodField()  #This field will be calculated using a custom method you define.We 
    trade_time_local = serializers.SerializerMethodField()  # SerializerMethodField() creates a read-only field in the serializer, not in the model.
    

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
        return super().to_internal_value(data)  #Calls the parent class's to_internal_value to handle the rest of the deserialization process.

#===============================================================================================================================

#Second serializer for FuturesTrade model
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

#Third serializer: MeSerializer for User model
class ExchangeCredentialCreateSerializer(serializers.ModelSerializer):#ModelSerializer auto-generates fields for model fields in Meta.fields (exchange, label, can_trade, can_transfer).
    # three extra fields added for input only (write_only=True) - not stored directly in the model
    # These are the “explicitly declared fields.”
    """
    Accepts plaintext once at the boundary, encrypts immediately with CryptoVault,
    saves to *_enc. Attaches the row to request.user. Never returns plaintext.
    """

    api_key = serializers.CharField(write_only=True) # The API key for the exchange account.     
    api_secret = serializers.CharField(write_only=True) # The API secret for the exchange account.
    passphrase = serializers.CharField(write_only=True, required=False, allow_blank=True) # Optional passphrase for exchanges that require it.
    # These fields are write-only because we never want to expose sensitive credentials in API responses.
    # These fields are accepted on create/update but never shown in API responses.

    class Meta:
        model = ExchangeCredential
        fields = ["exchange", "label", "api_key", "api_secret", "passphrase", "can_trade", "can_transfer"]

    def create(self, validated):
        v = CryptoVault()
        return ExchangeCredential.objects.create( # Create and return a new ExchangeCredential instance using the validated data.
            #validated is a dictionary of the validated input data.
            user=self.context["request"].user, #views passes the request in the serializer context. We use it to set the user field. 
            #We are injecting the currently authenticated user into the new ExchangeCredential instance.
            exchange=validated["exchange"], 
            label=validated.get("label","default"),
            api_key_enc=v.enc(validated["api_key"]),
            api_secret_enc=v.enc(validated["api_secret"]),
            passphrase_enc=v.enc(validated.get("passphrase","")) if validated.get("passphrase") else None,
            can_trade=validated.get("can_trade", True), #Default to True if not provided.because most users will want trading enabled.
            can_transfer=validated.get("can_transfer", False),#Default to False if not provided.because most users won’t need transfer capabilities.
        )
    
#===============================================================================================================================
#Fourth serializer: RegisterSerializer for User model SIGNUP
# User Serializer for creating new users with password validation and hashing.

class RegisterSerializer(serializers.ModelSerializer):
    """
    Public serializer used for user registration.

    - Ensures username/email uniqueness.
    - Runs Django's password validators.
    - Uses create_user() so password is hashed.
    """
    password = serializers.CharField( #This is a custom field for password input.
        #serializers.CharField declares a plain text field.
        write_only = True,# => This field is only for input (e.g., during registration) and will not be included in serialized output.
        trim_whitespace = False, # => clients can send a password with the request, but it will never be returned in the response payload. This is critical for security—your API never echoes passwords back.
        style = {"input_type": "password"}, # => This hint can be used by API clients (like browsable API) to render the input appropriately (e.g., as a password field).
      )#It will not show the password such as, it will show ******* instead of actual password to mask it.
    
    class Meta:
        model = User #The User model to serialize/deserialize.
        fields = ("id", "username", "email", "password")

    # ---- Username validation --------------------------------------
    # Ensures:
    # Duplicate usernames return 400 Bad Request
    # Frontend receives: { "username": ["Username already taken."] }

    def validate_username(self,value):# Ensure username is unique.
        #value is the username being validated.
        if User.objects.filter(username=value).exists(): #Check if a user with this username already exists in the database.
            # if a record is found, raise a validation error.
            #filter(username=value) makes a query to find users with the given username.
            #exists() checks if any such user exists.returns True if a match exists, False otherwise.
            raise serializers.ValidationError("Username already taken.")
        return value    #If no existing user is found, return the validated username.
    
    # ---- Email validation (optional field) -------------------------
    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value
    
    # ---- Password validation (Django validators) ---------------------
    def validate_password(self, value):  # Validate password using Django's built-in validators.
        # DRF stores the raw request payload on self.initial_data (that is an attribute in __init__ of the serializer clase) as soon as the serializer
        # is instantiated (RegisterSerializer(data=request.data)). Before validation finishes we
        # can read the submitted username from there, build an unsaved User instance with it, and
        # pass that stub to password_validation.validate_password so Django applies the global
        # password policy (length, similarity to username, etc.) against the exact values the user
        # typed. If any validator fails a ValidationError bubbles up, otherwise we return the
        # original password so create_user() can hash it later in create().
        user = User(username=self.initial_data.get("username", "")) #Create a temporary User instance with the submitted username.
        password_validation.validate_password(value, user) #Validate the password against Django's password policies.
        #password_validation is a Django module(you can find it in the library django.contrib.auth package) that provides functions to validate passwords according to configured validators.
        #From there we pull validate_password() which checks the password against the validators defined in our Django settings (like minimum length, complexity, similarity to username, etc.).
        #Errors are handled by DRF and returned as validation errors in the API response if any validator fails.
        return value
    
    # ---- Create user using create_user() ---------------------------
    #It hashes passwords securely
    #It sets user defaults
    #It respects your custom User model (if extended later)
    #We can't use User.objects.create() — it stores raw password (security disaster).

    def create(self,validated_data): # Create and return a new User instance using the validated data.
        #validated_data is a dictionary of DRF Library, where our field values have been validated, cleaned and saved.
        return User.objects.create_user( #Use create_user() to ensure password is hashed properly.
            username = validated_data["username"],
            email = validated_data.get("email") or "", #Email is optional; default to empty string if not provided.
            password = validated_data["password"],
        )

#===============================================================================================================================
#Fifth serializer: MeSerializer for User model

# ---------- /api/me/ -------------------------------------------------
#This serializer provides a minimal representation of the current user that's why is created here.
# And below is the view that uses it to return the authenticated user's info..
#Serializer to convert User model instances to/from JSON for the /api/me/ endpoint.
class MeSerializer(serializers.ModelSerializer):
    """
    Minimal representation of the current user.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")

        
    
    