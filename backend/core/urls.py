"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from api.views import SpotTradeViewSet, FuturesTradeViewSet
from django.http import HttpResponse

router = DefaultRouter() # => This router automatically generates URL patterns for our viewsets. We register our viewsets with specific URL prefixes.
router.register(r'spot-trades', SpotTradeViewSet, basename='spottrade' ) # => This line registers the SpotTradeViewSet with the router. The URL prefix 'spot-trades' means that all endpoints for this viewset will be accessible under /api/spot-trades/. The basename is used to name the URL patterns.
router.register(r'futures-trades', FuturesTradeViewSet, basename='futurestrade') # => This line registers the FuturesTradeViewSet with the router. The URL prefix 'futures-trades' means that all endpoints for this viewset will be accessible under /api/futures-trades/. The basename is used to name the URL patterns.

def home(request):
    return HttpResponse("✅ Welcome to the Trade Tracker API!")

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),      # ✅ Keeps the admin panel!
    path("api/", include(router.urls)),   # ✅ REST API at /api/...
]