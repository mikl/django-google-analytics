from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site


if getattr(settings, 'GOOGLE_ANALYTICS_MODEL', False):
    from google_analytics.models import Analytics


    class AnalyticsInline(admin.TabularInline):

        max_num = 1
        model = Analytics


    class SiteAdmin(BaseSiteAdmin):

        def __init__(self, *args, **kwargs):
            if not hasattr(self, 'inlines') or not self.inlines:
                self.inlines = [AnalyticsInline]
            else:
                self.inlines = list(self.inlines)
                self.inlines.append(AnalyticsInline)

            super(SiteAdmin, self).__init__(*args, **kwargs)


    try:
        admin.site.unregister(Site)
    except NotRegistered:
        pass

    admin.site.register(Site, SiteAdmin)
