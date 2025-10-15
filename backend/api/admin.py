from django.contrib import admin
from .models import SpotTrade, FuturesTrade
#This is the panel where you can view/edit your models in the Django admin interface.

# Register your models here.
admin.site.register(SpotTrade)
admin.site.register(FuturesTrade)
