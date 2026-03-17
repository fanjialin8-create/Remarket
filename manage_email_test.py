#!/usr/bin/env python
"""Test email sending - Run: python manage_email_test.py"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Commerce.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print('=== Email Config ===')
print('USE_REAL_EMAIL:', getattr(settings, 'USE_REAL_EMAIL', 'N/A'))
print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('EMAIL_HOST:', getattr(settings, 'EMAIL_HOST', ''))
print('EMAIL_PORT:', getattr(settings, 'EMAIL_PORT', ''))
print('EMAIL_HOST_USER:', getattr(settings, 'EMAIL_HOST_USER', ''))
print()

email = getattr(settings, 'EMAIL_HOST_USER', '') or '133873806@qq.com'
print(f'Sending test email to {email} ...')

try:
    send_mail(
        subject='ReMarket Test Email',
        message='If you receive this email, the configuration is correct!',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )
    print('OK - Email sent! Check inbox and spam folder')
except Exception as e:
    print('FAIL:', e)
    print()
    print('Gmail: Enable 2FA and create an app password at Google Account -> Security -> App passwords')
