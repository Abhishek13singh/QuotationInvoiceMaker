"""
WSGI config for invoice_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_project.settings')

application = get_wsgi_application()