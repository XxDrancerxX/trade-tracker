from django.db import models # Import the models module from django.db, which provides the base class and field types for defining database models.
from django.contrib.auth.models import User # Import the built-in User model from Django's authentication system.
from django.utils import timezone # Import timezone utilities to handle date and time fields correctly with timezone awareness.
#------------------------------------------------------------------------------------------------------------------------------
# Create your models here.
#Super user:
# superuser
# super@user.com
# 123456
#------------------------------------------------------------------------------------------------------------------------------#For the fields trade_time and created_at, we use DateTimeField to store date and time information.

#For the fields trade_time and created_at, we use DateTimeField to store date and time information.
# trade_time records when the trade actually happened, while created_at automatically records when the trade entry was created in the database.
# We set default=timezone.now for trade_time to automatically set it
# to the current date and time when a new trade is created, unless specified otherwise.
#------------------------------------------------------------------------------------------------------------------------------

#We put models.Model in each model to tell Django that these classes are database models.
#The classes models inherits everything from models.Model.
# This gives us all the built-in functionality to create, read, update, and delete records in the database.
# Each class variable (like symbol, price, amount) defines a database column with a specific type and constraints.
# For example, CharField is for short text, DecimalField is for precise decimal numbers,
# ForeignKey creates a relationship to another model (like User), and DateTimeField is for date/time values.
#This is what basically transforms classes into database tables with rows and columns.
#===============================================================================================================================

class ExchangeCredential(models.Model):#Secure place to store each user’s encrypted API key/secret/passphrase (*_enc bytes). One row per connected exchange account.
    """
    Stores per-user exchange credentials encrypted.so the user can connect to exchanges via our app and many others activities.
    Each user can have multiple ExchangeCredential entries (e.g., one for Coinbase, one for Binance).
    Each entry stores the exchange name (e.g., "coinbase-exchange"), a label (e.g., "default"), and the encrypted API key/secret/passphrase.
    DO NOT store raw secrets; encrypt via CryptoVault.
    """
    #If you don't see null=True or blank=True, the field is required.

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchange_creds") # Links each ExchangeCredential to a specific User
    # The user field establishes a many-to-one relationship with the User model. This means each user can have multiple exchange credentials, but each credential belongs to one user.
    # The on_delete=models.CASCADE argument ensures that if a user is deleted, all their associated exchange credentials are also deleted.
    # The related_name="exchange_creds" argument allows us to access a user's exchange credentials using user.exchange_creds.all().
    exchange = models.CharField(max_length=32)  # Stores which exchange this credential is for (e.g., "coinbase-exchange", "binance", etc.). max_length=32 limits the length to 32 characters.
    # models.CharField is used for short text fields, it requires max_length to work. This field is required (no null=True or blank=True), so every ExchangeCredential must specify an exchange.
    # This field does not have a default value, so it must be provided when creating a new ExchangeCredential.
    label = models.CharField(max_length=64, default="default") # A user can have multiple credentials per exchange, if no label is provided when creating an instance, Django will set the attribute to "default".
    api_key_enc = models.BinaryField()      # encrypted bytes stores raw binary data.
    api_secret_enc = models.BinaryField()   # encrypted bytes
    passphrase_enc = models.BinaryField(null=True, blank=True) # encrypted bytes, some exchanges (like Coinbase Pro) require a passphrase in addition to API key/secret.
    can_trade = models.BooleanField(default=True) # Allow this credential to place/modify/cancel orders and run reads.
    can_transfer = models.BooleanField(default=False) #allow this credential to withdraw/transfer funds (on-chain or to another account).
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set the field to now when the object is first created. Useful for tracking when the credential was added.


class SpotTrade(models.Model):    
    def __str__(self):
        return f"{self.user.username} - {self.symbol} = {self.side} - @ {self.price}"
    
    symbol = models.CharField(max_length=10) # stores the trade instrument/ticker (e.g., "BTCUSD", "ETH", "BTC-USD") for each SpotTrade.
    price = models.DecimalField(max_digits=10,decimal_places=2) # => This field stores the price at which the trade was executed. DecimalField is used for precise decimal numbers, which is important for financial data.
    # max_digits=10 means the number can have up to 10 digits in total, and decimal_places=2 means 2 of those digits can be after the decimal point.
    amount = models.DecimalField(max_digits=20,decimal_places=8)
    trade_time = models.DateTimeField(default=timezone.now, db_index=True)   # DateTimefiled creates a date/time column in the database.
    # => This field records the exact date and time when the trade occurred. We set default=timezone.now to automatically use the current date and time if none is provided.
    # db_index=True creates a database index on this field, which speeds up queries that filter or sort by trade_time
    user = models.ForeignKey(User, on_delete=models.CASCADE) # => This creates a relationship between the SpotTrade and User models. Each trade is linked to a specific user. If the user is deleted, all their trades will also be deleted (cascade delete).
    created_at = models.DateTimeField(auto_now_add=True) # => This field automatically records the date and time when a trade is created. It’s set once when the object is first created and never changes.
    SIDE_CHOICES = [ # This defines the possible choices for the side field.
    ("BUY", "Buy"),
    ("SELL", "Sell"),
    ] 

    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    exchange = models.CharField(max_length=20)
    currency = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

class FuturesTrade(models.Model):    
    def __str__(self):
        return f"{self.user.username} - {self.symbol} = {self.side} - @ {self.price}"
    
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    liquidation_price = models.DecimalField(max_digits=10, decimal_places=2)
    leverage = models.IntegerField()
    pnl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exchange = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=20,decimal_places=8)
    trade_time = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    SIDE_CHOICES = [
    ("BUY", "Buy"),
    ("SELL", "Sell"),
    ] 

    side = models.CharField(max_length=4, choices=SIDE_CHOICES)   
    currency = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

class TransferRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transfer_requests")
    cred = models.ForeignKey("api.ExchangeCredential", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.CharField(max_length=16)
    to_address = models.CharField(max_length=128)
    status = models.CharField(max_length=16, default="PENDING")  # PENDING/APPROVED/REJECTED/EXECUTED
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_transfers")
    approved_at = models.DateTimeField(null=True, blank=True)
    idempotency_key = models.CharField(max_length=64, unique=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=64)  # e.g., "TRANSFER_REQUEST", "APPROVE", "EXECUTE"
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
