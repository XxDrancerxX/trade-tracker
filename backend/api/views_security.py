from rest_framework.decorators import api_view, permission_classes, throttle_classes
# api_view to define function-based views for our API endpoints.
# permission_classes to set access control on our views.
# throttle_classes to apply rate limiting to our views.
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# isAuthenticated ensures that only logged-in users can access the view.
# IsAdminUser restricts access to admin users only.
from rest_framework.throttling import UserRateThrottle # to define custom rate limiting based on user. 
from rest_framework.response import Response # to return HTTP responses with data in our API views.
from django.shortcuts import get_object_or_404 # to retrieve database objects or return 404 if not found.
from api.models import ExchangeCredential 
from api.exchanges.coinbase_exchange import build_exchange_adapter # to create exchange adapter instances for interacting with specific exchanges.

#===============================================================================================================================
# Example view with strict rate limiting for authenticated users only to list recent fills from an exchange. 
# Each user can make up to 10 requests per minute to this endpoint.
# Define a custom throttle class with a strict rate limit.


class StrictThrottle(UserRateThrottle): #inherits from UserRateThrottle to create a custom throttle class.
    rate = "10/min" # sets the rate limit to 10 requests per minute.

# We use a class to override the default rate limit for this specific view whithout changing global settings.

@api_view(["GET"]) #this view accepts only GET requests.
@permission_classes([IsAuthenticated]) # only authenticated users can access this view.
@throttle_classes([StrictThrottle])

def list_fills(request, cred_id): #It handles requests to list recent trade fills for a given exchange credential.
    #request is the HTTP request object.
    #cred_id is the ID of the exchange credential to fetch fills for.
    cred = get_object_or_404(ExchangeCredential, id=cred_id, user=request.user) # retrieves the ExchangeCredential object for the given cred_id that belongs to the requesting user.
    adapter = build_exchange_adapter(cred) # builds an exchange adapter using the retrieved credential.
    fills = adapter.fills(limit=50) # fetches the most recent 50 fills from the exchange via the adapter.
    return Response({"count": len(fills), "fills": fills[:5]}) # returns an HTTP response containing the count of fills and the first 5 fills.