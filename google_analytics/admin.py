from django.conf import settings
from django.contrib import admin

if getattr(settings, 'GOOGLE_ANALYTICS_MODEL', False):
    from google_analytics.models import Analytics
    admin.site.register(Analytics)

