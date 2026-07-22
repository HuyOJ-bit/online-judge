"""ASGI config (not used on PythonAnywhere, provided for completeness)."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onlinejudge.settings")

application = get_asgi_application()
