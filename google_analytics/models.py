from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


if getattr(settings, 'GOOGLE_ANALYTICS_MODEL', False):
    class Analytics(models.Model):
        site = models.OneToOneField('sites.Site', verbose_name=_('site'))
        code = models.CharField(_('analytics code'), blank=True,
            max_length=100)

        class Meta:
            db_table = 'google_analytics'
            verbose_name = _('Google Analytics')
            verbose_name_plural = _('Google Analytics')

        def __unicode__(self):
            return self.code
