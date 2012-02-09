# -*- coding: utf-8 -*-
from unidecode import unidecode
from django.conf import settings
from django.test import TestCase, Client

class BaseTestCase(TestCase):
    def _setup_settings(self, custom_settings):
        original_settings = {}
        for setting_name, value in custom_settings.items():
            if hasattr(settings, setting_name):
                original_settings[setting_name] = getattr(settings,
                                                          setting_name)
            setattr(settings, setting_name, value)
        return original_settings

    def _teardown_settings(self, original_settings, custom_settings=None):
        custom_settings = custom_settings or {}
        for setting_name, value in original_settings.items():
            setattr(settings, setting_name, value)
            if setting_name in custom_settings:
                del custom_settings[setting_name]
        for setting_name, value in custom_settings.items():
            delattr(settings, setting_name)


class ViewsTestCase(BaseTestCase):
    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data, follow=False)
        self.assertEqual(response.status_code, status_code,
            u'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url.decode('utf-8'), args, kwargs, status_code, response.status_code,
                unidecode(response.content).decode('utf-8')))
        return response

    def _test_GET_status(self, url, *args, **kwargs):
        return self._test_status(url, 'get', *args, **kwargs)

    def _test_POST_status(self, url, *args, **kwargs):
        kwargs['status_code'] = kwargs.get('status_code', 302)
        return self._test_status(url, 'post', *args, **kwargs)
