from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#Super user:
# superuser
# super@user.com
# 123456

class Trade(models.Model):    
    def __str__(self):
        return f"{self.user.username} - {self.symbol} = {self.side} - @ {self.price}"
    
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.DecimalField(max_digits=20,decimal_places=8)
    trade_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    SIDE_CHOICES = [
    ("BUY", "Buy"),
    ("SELL", "Sell"),
    ] 
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    exchange = models.CharField(max_length=20)
    currency = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

