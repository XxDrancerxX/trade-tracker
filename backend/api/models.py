from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
#Super user:
# superuser
# super@user.com
# 123456


#For the fields trade_time and created_at, we use DateTimeField to store date and time information.
# trade_time records when the trade actually happened, while created_at automatically records when the trade entry was created in the database.
# We set default=timezone.now for trade_time to automatically set it
# to the current date and time when a new trade is created, unless specified otherwise.


class SpotTrade(models.Model):    
    def __str__(self):
        return f"{self.user.username} - {self.symbol} = {self.side} - @ {self.price}"
    
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=8)
    trade_time = models.DateTimeField(default=timezone.now, db_index=True)   # => db_index=True creates a database index on this field, which speeds up queries that filter or sort by trade_time.
    user = models.ForeignKey(User, on_delete=models.CASCADE) # => This creates a relationship between the SpotTrade and User models. Each trade is linked to a specific user. If the user is deleted, all their trades will also be deleted (cascade delete).
    created_at = models.DateTimeField(auto_now_add=True) # => This field automatically records the date and time when a trade is created. It’s set once when the object is first created and never changes.
    SIDE_CHOICES = [
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

