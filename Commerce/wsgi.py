"""
WSGI config for Commerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from pathlib import Path

# Load .env before Django starts (for PythonAnywhere etc.)
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / '.env')
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Commerce.settings')

application = get_wsgi_application()
