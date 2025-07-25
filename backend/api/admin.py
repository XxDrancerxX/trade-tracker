from django.contrib import admin
from .models import SpotTrade, FuturesTrade

# Register your models here.
admin.site.register(SpotTrade)
admin.site.register(FuturesTrade)
