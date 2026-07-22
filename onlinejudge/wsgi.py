"""
WSGI config for Online Judge.

On PythonAnywhere you do NOT use this file directly — you edit the
auto-generated WSGI file in the Web tab (see DEPLOY_PYTHONANYWHERE.md),
which imports the application the same way as below.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onlinejudge.settings")

application = get_wsgi_application()
