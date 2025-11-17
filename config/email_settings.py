# Development Email Configuration - prints emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sophistican Laundry Logistics <noreply@sophisticanlaundry.com>'

# For production with Amazon SES, configure in local_settings.py or environment variables:
"""
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'  # Set in env or local_settings.py
AWS_SECRET_ACCESS_KEY = 'your-secret-key'  # Set in env or local_settings.py
AWS_SES_REGION_NAME = 'your-region'  # e.g., 'us-east-1'
AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
AWS_SES_AUTO_THROTTLE = 0.5  # Optional: throttle to 2 emails/second
"""

