# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from ....cart.models import Cart, CART_SESSION_KEY
from ....delivery.tests import TestDeliveryProvider
from ....order import handler as order_handler
from ....order.models import Order
from ....payment import ConfirmationFormNeeded
from ....payment.tests import TestPaymentProvider
from ....product import handler as product_handler
from ....product.tests import DeadParrot

from satchless.product.tests.pricing import FiveZlotyPriceHandler
from satchless.pricing import handler

from ..common.views import prepare_order, confirmation
from . import views

urlpatterns = patterns('',
    url(r'^cart/', include('satchless.cart.urls')),
    url(r'^checkout/', include('satchless.contrib.checkout.singlestep.urls')),
)

class TestPaymentProviderWithConfirmation(TestPaymentProvider):
    def confirm(self, order):
        raise ConfirmationFormNeeded(action='http://test.payment.gateway.example.com')


class CheckoutTest(TestCase):
    urls = 'satchless.contrib.checkout.singlestep.tests'

    def _setup_settings(self, custom_settings):
        original_settings = {}
        for setting_name, value in custom_settings.items():
            if hasattr(settings, setting_name):
                original_settings[setting_name] = getattr(settings, setting_name)
            setattr(settings, setting_name, value)
        return original_settings

    def _teardown_settings(self, original_settings, custom_settings=None):
        custom_settings = custom_settings or {}
        for setting_name, value in custom_settings.items():
            if setting_name in original_settings:
                setattr(settings, setting_name, value)
            else:
                delattr(settings, setting_name)

    def setUp(self):
        self.parrot = DeadParrot.objects.create(slug='parrot',
                                                species='Hyacinth Macaw')
        self.dead_parrot = self.parrot.variants.create(color='blue',
                                                       sku='P-BL-D',
                                                       looks_alive=False)

        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.add_to_cart_handler',),
            'SATCHLESS_DELIVERY_PROVIDERS': [TestDeliveryProvider],
            'SATCHLESS_PAYMENT_PROVIDERS': [TestPaymentProviderWithConfirmation],
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        product_handler.init_queue()
        order_handler.init_queues()
        self.anon_client = Client()
        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        handler.pricing_queue = handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)
        product_handler.init_queue()
        order_handler.init_queues()
        handler.pricing_queue = handler.PricingQueue(*self.original_handlers)

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data)
        self.assertEqual(response.status_code, status_code,
            'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url.decode('utf-8'), args, kwargs, status_code, response.status_code,
                response.content.decode('utf-8')))
        return response

    def _get_or_create_cart_for_client(self, client, typ='satchless_cart'):
        self._test_status(reverse('satchless-cart-view'),
                          client_instance=client)
        return Cart.objects.get(pk=client.session[CART_SESSION_KEY % typ],
                                typ=typ)

    def _get_or_create_order_for_client(self, client):
        self._test_status(reverse(prepare_order), method='post',
                          client_instance=client, status_code=302)
        order_pk = client.session.get('satchless_order', None)
        return Order.objects.get(pk=order_pk)

    def _get_order_items(self, order):
        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant',
                                                       'quantity'))
        return order_items

    def test_checkout_view_passes_with_correct_data(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.set_quantity(self.dead_parrot, 1)
        order = self._get_or_create_order_for_client(self.anon_client)

        response = self._test_status(reverse(views.checkout,
                                             kwargs={'order_token':
                                                     order.token}),
                                     client_instance=self.anon_client,
                                     data={'email': 'foo@example.com'})
        dg = response.context['delivery_group_forms']
        data = {'billing_first_name': 'First',
                'billing_last_name': 'Last',
                'billing_street_address_1': 'Via Rodeo 1',
                'billing_city': 'Beverly Hills',
                'billing_country': 'US',
                'billing_country_area': 'AZ',
                'billing_phone': '555-555-5555',
                'billing_postal_code': '90210'}
        for g, typ, form in dg:
            data[form.add_prefix('email')] = 'foo@example.com'

        response = self._test_status(reverse(views.checkout,
                                             kwargs={'order_token':
                                                     order.token}),
                                     client_instance=self.anon_client,
                                     status_code=302, method='post', data=data,
                                     follow=True)

        order = Order.objects.get(pk=order.pk)

        self.assertRedirects(response, reverse(confirmation,
                                               kwargs={'order_token':
                                                       order.token}))
        self.assertEqual(order.status, 'payment-pending')


    def test_confirmation_view_redirects_when_order_or_payment_is_missing(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.set_quantity(self.dead_parrot, 1)

        order = self._get_or_create_order_for_client(self.anon_client)
        # without payment
        self._test_status(reverse(confirmation, kwargs={'order_token':
                                                        order.token}),
                          client_instance=self.anon_client, status_code=302)
        # finish checkout view
        response = self._test_status(reverse(views.checkout,
                                             kwargs={'order_token':
                                                     order.token}),
                                     client_instance=self.anon_client,
                                     data={'email': 'foo@example.com'})
        dg = response.context['delivery_group_forms']
        data = {'billing_first_name': 'First',
                'billing_last_name': 'Last',
                'billing_street_address_1': 'Via Rodeo 1',
                'billing_city': 'Beverly Hills',
                'billing_country': 'US',
                'billing_country_area': 'AZ',
                'billing_phone': '555-555-5555',
                'billing_postal_code': '90210'}
        for g, typ, form in dg:
            data[form.add_prefix('email')] = 'foo@example.com'

        response = self._test_status(reverse(views.checkout,
                                             kwargs={'order_token':
                                                     order.token}),
                                     client_instance=self.anon_client,
                                     status_code=302, method='post', data=data,
                                     follow=True)

        self._test_status(reverse(confirmation, kwargs={'order_token':
                                                        order.token}),
                          client_instance=self.anon_client,
                          status_code=200)
