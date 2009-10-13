from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template import Library, Node, TemplateSyntaxError, Variable, \
                            loader
from django.utils.safestring import mark_safe


register = Library()


class AnalyticsNode(Node):
    def __init__(self, code=None):
        self.code = code

    def render(self, context):
        # Tries to get code value as template tag argument
        if self.code is not None:
            code = Variable(self.code).resolve(context)
        else:
            code = self.code

        # If Google Analytics code is empty tries to load it from current
        # site object
        if not code:
            site = Site.objects.get_current()

            try:
                code = site.analytics.code
            except ObjectDoesNotExist:
                # If Analytics model object has not been created.
                pass
            except AttributeError:
                # If the Analytics model is not loaded.
                pass

        if not code:
            return u''

        return mark_safe(loader.render_to_string(
            'google_analytics/analytics_template.html',
            {'analytics_code': code},
        ))


def do_analytics(parser, token):
    code = None
    contents = token.split_contents()

    if len(contents) == 2:
        code = contents[1]
    elif len(contents) != 1:
        raise TemplateSyntaxError, 'Usage: {% analytics ["UA-xxxxxx-x"] %}'

    return AnalyticsNode(code)
register.tag('analytics', do_analytics)
