"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
#async gateway for websockets/long-polling/async views (Uvicorn/Daphne).
#core/asgi.py: entrypoint for ASGI servers.
# ASGI (Asynchronous Server Gateway Interface)
# The newer standard.
# Supports both sync and async requests.
# Can handle websockets, real-time updates, background tasks.
# Run with Uvicorn or Daphne.
# Django supports both (ASGI since Django 3.0).

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()
