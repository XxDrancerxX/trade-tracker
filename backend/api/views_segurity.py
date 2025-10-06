from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import ExchangeCredential
from api.exchanges.coinbase_exchange import build_exchange_adapter


class StrictThrottle(UserRateThrottle):
    rate = "10/min"

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@throttle_classes([StrictThrottle])
def list_fills(request, cred_id):
    cred = get_object_or_404(ExchangeCredential, id=cred_id, user=request.user)
    adapter = build_exchange_adapter(cred)
    fills = adapter.fills(limit=50)
    return Response({"count": len(fills), "fills": fills[:5]})
