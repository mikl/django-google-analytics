import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import Context, Template, TemplateSyntaxError
from django.test import Client


if getattr(settings, 'GOOGLE_ANALYTICS_MODEL', False):
    from google_analytics.models import Analytics


    TEST_CODE = 'UA-123456-7'
    TEST_CODE_ANOTHER = 'UA-765432-1'
    TEST_EMAIL = 'email@domain.com'
    TEST_PASSWORD = 'password'
    TEST_USERNAME = 'username'


    class TestAnalytics(unittest.TestCase):

        def setUp(self):
            # Creates admin user
            admin = User.objects.create_user(username=TEST_USERNAME,
                                             password=TEST_PASSWORD,
                                             email=TEST_EMAIL)
            admin.is_staff, admin.is_superuser = True, True
            admin.save()

            # Clean-up previous analytics codes
            Analytics.objects.all().delete()

            self.admin = admin
            self.client = Client()
            self.site = Site.objects.get_current()

        def tearDown(self):
            self.admin.delete()

        def test_admin(self):
            client = self.client
            site = self.site

            client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
            response = client.get('/admin/sites/site/%d/' % site.pk)
            self.assertEqual(response.status_code, 200)

            html = response.content

            assert 'Google Analytics' in html, html
            assert 'Analytics code' in html, html
            assert 'name="analytics-0-code"' in html, html

            # Adds Google Analytics code to current site
            response = client.post('/admin/sites/site/%d/' % site.pk,
                                   {
                                       'name': site.name,
                                       'domain': site.domain,
                                       'analytics-INITIAL_FORMS': '0',
                                       'analytics-TOTAL_FORMS': '1',
                                       'analytics-0-id': '0',
                                       'analytics-0-site': '%d' % site.pk,
                                       'analytics-0-code': TEST_CODE,
                                   })
            self.assertEqual(response.status_code, 302)

            analytics = Analytics.objects.get(code=TEST_CODE)
            self.assertEqual(analytics.site, site)

            # Edits Google Analytics code of current site
            response = client.post('/admin/sites/site/%d/' % site.pk,
                                   {
                                       'name': site.name,
                                       'domain': site.domain,
                                       'analytics-INITIAL_FORMS': '1',
                                       'analytics-TOTAL_FORMS': '1',
                                       'analytics-0-id': '%d' % analytics.pk,
                                       'analytics-0-site': '%d' % site.pk,
                                       'analytics-0-code': TEST_CODE_ANOTHER,
                                   },
                                   follow=True)
            self.assertEqual(response.status_code, 302)

            analytics = Analytics.objects.get(code=TEST_CODE_ANOTHER)
            self.assertEqual(analytics.site, site)

            # Clean-up Google Analytics code
            response = client.post('/admin/sites/site/%d/' % site.pk,
                                   {
                                       'name': site.name,
                                       'domain': site.domain,
                                       'analytics-INITIAL_FORMS': '1',
                                       'analytics-TOTAL_FORMS': '1',
                                       'analytics-0-id': '%d' % analytics.pk,
                                       'analytics-0-site': '%d' % site.pk,
                                       'analytics-0-code': '',
                                   })
            self.assertEqual(response.status_code, 302)

            analytics = Analytics.objects.get(code='')
            self.assertEqual(analytics.site, site)

            # Deletes Google Analytics
            old_counter = Analytics.objects.count()
            response = client.post('/admin/sites/site/%d/' % site.pk,
                                   {
                                       'name': site.name,
                                       'domain': site.domain,
                                       'analytics-INITIAL_FORMS': '1',
                                       'analytics-TOTAL_FORMS': '1',
                                       'analytics-0-DELETE': 'on',
                                       'analytics-0-id': '%d' % analytics.pk,
                                       'analytics-0-site': '%d' % site.pk,
                                       'analytics-0-code': '',
                                   })
            self.assertEqual(response.status_code, 302)

            new_counter = Analytics.objects.count()

            self.assertEqual(new_counter + 1, old_counter)
            self.assertRaises(Analytics.DoesNotExist,
                              Analytics.objects.get,
                              site=site)

        def test_models(self):
            old_counter = Analytics.objects.count()
            analytics = Analytics.objects.create(site=self.site,
                                                 code=TEST_CODE)

            new_counter = Analytics.objects.count()
            self.assertEqual(new_counter - 1, old_counter)
            self.assertEqual(unicode(analytics), u'%s' % TEST_CODE)

            analytics.code = ''
            analytics.save()

            self.assertEqual(unicode(analytics), u'')

            self.assertRaises(Exception,
                              Analytics.objects.create,
                              site=self.site,
                              code=TEST_CODE_ANOTHER)

        def test_templates(self):
            context = Context({})
            template = Template('{% load analytics %}{% analytics %}')

            rendered = template.render(context)
            self.assertEqual(rendered, '')

            Analytics.objects.create(site=self.site,
                                     code=TEST_CODE)
            rendered = template.render(context)

            assert TEST_CODE in rendered, rendered

            template = Template(
                '{%% load analytics %%}{%% analytics "%s" %%}' % TEST_CODE
            )
            rendered = template.render(context)

            assert TEST_CODE in rendered, rendered

            error_template = '{%% load analytics %%}'\
                             '{%% analytics "%s" "%s" %%}' % (TEST_CODE,
                                                              TEST_CODE)
            self.assertRaises(TemplateSyntaxError,
                              Template,
                              error_template)
