# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from satchless.product.tests import DeadParrot

from satchless.cart.models import Cart, CART_SESSION_KEY
from satchless.order.models import Order
import satchless.order.handler
import satchless.product.handler

from ..common.views import prepare_order
from . import views

# force to create models
from ....delivery.tests import TestDeliveryProvider
from ....payment.tests import TestPaymentProvider

class CheckoutTest(TestCase):
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
        self.parrot = DeadParrot.objects.create(slug='parrot', species="Hyacinth Macaw")
        self.dead_parrot = self.parrot.variants.create(color='blue', looks_alive=False)

        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.add_to_cart_handler',),
            'SATCHLESS_DELIVERY_PROVIDERS': [TestDeliveryProvider],
            'SATCHLESS_PAYMENT_PROVIDERS': [TestPaymentProvider],
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        satchless.product.handler.init_queue()
        satchless.order.handler.init_queues()
        self.anon_client = Client()

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)
        satchless.product.handler.init_queue()
        satchless.order.handler.init_queues()

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
        self._test_status(reverse('satchless-cart-view'), client_instance=client)
        return Cart.objects.get(pk=client.session[CART_SESSION_KEY % typ], typ=typ)

    def _get_or_create_order_for_client(self, client):
        self._test_status(reverse(prepare_order), method='post',
                          client_instance=client, status_code=302)
        order_pk = client.session.get('satchless_order', None)
        return Order.objects.get(pk=order_pk)

    def _get_order_items(self, order):
        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant', 'quantity'))
        return order_items

    def test_checkout_view_redirects_when_order_is_missing(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.set_quantity(self.dead_parrot, 1)

        self._test_status(reverse(views.checkout), client_instance=self.anon_client, status_code=302)
        self._get_or_create_order_for_client(self.anon_client)
        self._test_status(reverse(views.checkout), client_instance=self.anon_client, status_code=200)

    def test_checkout_view_passes_with_correct_data(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.set_quantity(self.dead_parrot, 1)
        self._get_or_create_order_for_client(self.anon_client)

        response = self._test_status(reverse(views.checkout), client_instance=self.anon_client,
                                     data={'email': 'foo@example.com'})
        dg = response.context['delivery_groups_forms']
        data = {}
        for g, typ, form in dg:
            data[form.add_prefix('email')] = 'foo@example.com'

        self._test_status(reverse(views.checkout), client_instance=self.anon_client,
                          status_code=302, method='post', data=data)

