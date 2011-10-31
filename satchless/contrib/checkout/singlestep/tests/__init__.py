# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client

from .....checkout.tests import BaseCheckoutAppTests
from .....delivery.tests import TestDeliveryProvider
from .....order import handler as order_handler
from .....payment import ConfirmationFormNeeded
from .....payment.tests import TestPaymentProvider
from .....pricing import handler as pricing_handler
from .....product import handler as product_handler
from .....product.tests import DeadParrot
from .....product.tests.pricing import FiveZlotyPriceHandler

from ..app import checkout_app
from .....cart.tests import TestCart
from .....order.tests import TestOrder


class TestPaymentProviderWithConfirmation(TestPaymentProvider):
    def confirm(self, order, typ=None):
        raise ConfirmationFormNeeded(action='http://test.payment.gateway.example.com')


class App(BaseCheckoutAppTests):
    checkout_app = checkout_app
    urls = BaseCheckoutAppTests.MockUrls(checkout_app=checkout_app)

    def setUp(self):
        checkout_app.cart_model = TestCart
        checkout_app.order_model = TestOrder
        self.parrot = DeadParrot.objects.create(slug='parrot',
                                                species='Hyacinth Macaw')
        self.dead_parrot = self.parrot.variants.create(color='blue',
                                                       looks_alive=False)

        satchless_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.add_to_cart_handler',),
            'TEMPLATE_DIRS': (os.path.join(satchless_dir, 'category', 'templates'),
                              os.path.join(satchless_dir, 'order', 'templates'),
                              os.path.join(satchless_dir, 'cart', 'templates'),
                              os.path.join(satchless_dir, 'cart', 'templates'),
                              os.path.join(os.path.join(os.path.dirname(__file__),
                                                        'templates')),
                              os.path.join(os.path.join(os.path.dirname(__file__), '..',
                                                        'templates'))),
            'TEMPLATE_LOADERS': (
                'django.template.loaders.filesystem.Loader',
            )
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        product_handler.init_queue()
        order_handler.delivery_queue = order_handler.DeliveryQueue(TestDeliveryProvider)
        order_handler.payment_queue = order_handler.PaymentQueue(TestPaymentProviderWithConfirmation)
        self.anon_client = Client()
        self.original_pricing_handlers = settings.SATCHLESS_PRICING_HANDLERS
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)
        product_handler.init_queue()
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(*self.original_pricing_handlers)

    def test_checkout_view_passes_with_correct_data(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.replace_item(self.dead_parrot, 1)
        order = self._get_or_create_order_for_client(self.anon_client)

        response = self._test_status(reverse('checkout:checkout',
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

        response = self._test_status(self.checkout_app.reverse('checkout',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     client_instance=self.anon_client,
                                     status_code=302, method='post', data=data,
                                     follow=True)

        order = self.checkout_app.order_model.objects.get(pk=order.pk)

        self.assertRedirects(response, reverse('checkout:confirmation',
                                               kwargs={'order_token':
                                                       order.token}))
        self.assertEqual(order.status, 'payment-pending')


    def test_confirmation_view_redirects_when_order_or_payment_is_missing(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.replace_item(self.dead_parrot, 1)

        order = self._get_or_create_order_for_client(self.anon_client)
        # without payment
        self._test_status(reverse('checkout:confirmation',
                                  kwargs={'order_token': order.token}),
                          client_instance=self.anon_client, status_code=302)
        # finish checkout view
        response = self._test_status(self.checkout_app.reverse('checkout',
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

        response = self._test_status(self.checkout_app.reverse('checkout',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     client_instance=self.anon_client,
                                     status_code=302, method='post', data=data,
                                     follow=True)

        self._test_status(self.checkout_app.reverse('confirmation',
                                                    kwargs={'order_token':
                                                            order.token}),
                          client_instance=self.anon_client,
                          status_code=200)