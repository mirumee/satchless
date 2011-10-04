# -*- coding: utf-8 -*-
from django.test import TestCase, Client

class ViewTestCase(TestCase):
    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data, follow=False)
        self.assertEqual(response.status_code, status_code,
            'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url.decode('utf-8'), args, kwargs, status_code, response.status_code,
                response.content.decode('utf-8')))
        return response

    def _test_GET_status(self, url, *args, **kwargs):
        return self._test_status(url, 'get', *args, **kwargs)

    def _test_POST_status(self, url, *args, **kwargs):
        kwargs['status_code'] = kwargs.get('status_code', 302)
        return self._test_status(url, 'post', *args, **kwargs)