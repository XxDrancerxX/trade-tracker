"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
#WSGI (Web Server Gateway Interface)
#classic sync gateway. Use with Gunicorn/uWSGI (CPU-bound, simpler).
#core/wsgi.py: entrypoint for WSGI servers.
#WSGI (Web Server Gateway Interface)
# The old standard for Python web apps.
# Handles synchronous requests (one at a time per worker).
# Commonly run with Gunicorn or uWSGI.
# Works fine for APIs, but no native support for websockets or async features.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
