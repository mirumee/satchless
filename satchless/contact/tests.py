# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from .models import *

class ContactTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="testuser")
        self.user2 = User.objects.create(username="testlooser")
        self.user1.set_password(u"pasło")
        self.user1.save()
        self.user2.set_password(u"hasword")
        self.user2.save()

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data)
        self.assertEqual(response.status_code, status_code,
            'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url, args, kwargs, status_code, response.status_code, response.content
            )
        )
        return response

    def test_customer_creation(self):
        c1 = Customer.objects.get_or_create_for_user(self.user1)
        c2 = Customer.objects.get_or_create_for_user(self.user1)
        self.assertEqual(c1, c2)
        self.assertEqual(c1.email, self.user1.email)

    def test_address_creation(self):
        c1 = Customer.objects.get_or_create_for_user(self.user1)
        a1 = c1.addressbook.create(alias="Mirumee",
                full_name="Test User", street_address_1="pl. Solny 13/42",
                city=u"Wrocław", postal_code="50-061", country='PL')
        self.assertEqual(a1.customer.user, self.user1)
        self.assertEqual(a1.alias, unicode(a1))

    def test_views(self):
        Customer.objects.get_or_create_for_user(self.user1)
        cli_anon = Client()
        cli_user1 = Client()
        self.assert_(cli_user1.login(username="testuser", password=u"pasło"))
        cli_user2 = Client()
        self.assert_(cli_user2.login(username="testlooser", password=u"hasword"))

        self._test_status(reverse('satchless-contact-my-contact'),
                client_instance=cli_anon, status_code=302)
        self._test_status(reverse('satchless-contact-my-contact'),
                client_instance=cli_user1, status_code=200)
        self._test_status(reverse('satchless-contact-my-contact'),
                client_instance=cli_user2, status_code=200)


        self._test_status(reverse('satchless-contact-address-new'),
                client_instance=cli_user1, status_code=200)
        self._test_status(reverse('satchless-contact-address-new'),
                client_instance=cli_user1, method='post', status_code=302,
                data={'alias': "Mirumee", 'full_name': "Test User",
                    'street_address_1': "pl. Solny 13/42", 'country_area': u'Dolnośląskie',
                    'city': u"Wrocław", 'postal_code': "50-061", 'country': 'PL',
                    'set_as_default_billing': '1', 'set_as_default_shipping': '1'})

        c2 = Customer.objects.get_or_create_for_user(self.user2)
        a2 = c2.addressbook.create(alias="Biuro",
                full_name=u"Józef Tkaczuk", company_name="Sejm RP",
                street_address_1=u"ul. Wiejska 4/6/8", city="Warszawa",
                postal_code="00-902", country='PL')

        self._test_status(reverse('satchless-contact-address-edit', kwargs={'address_pk': a2.pk}),
                client_instance=cli_anon, status_code=302)
        self._test_status(reverse('satchless-contact-address-edit', kwargs={'address_pk': a2.pk}),
                client_instance=cli_user1, status_code=404)
        self._test_status(reverse('satchless-contact-address-edit', kwargs={'address_pk': a2.pk}),
                client_instance=cli_user2, status_code=200)


