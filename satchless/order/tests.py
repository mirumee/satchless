# -*- coding: utf-8 -*-
from decimal import Decimal
import os

from django.contrib.auth.models import User
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.test import Client

from .app import MagicOrderApp
from ..cart.tests import cart_app
from ..pricing import handler
from ..product.tests import DeadParrot
from ..product.tests.pricing import FiveZlotyPriceHandler
from ..util.tests import ViewsTestCase

class TestOrderApp(MagicOrderApp):
    pass


order_app = TestOrderApp(cart_app=cart_app)


class OrderTest(ViewsTestCase):
    class urls:
        urlpatterns = patterns('',
            url(r'^order/', include(order_app.urls)),
        )

    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue = self.macaw.variants.create(color='blue',
                                                     looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue',
                                                          looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white',
                                                              looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white',
                                                              looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue',
                                                             looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue',
                                                             looks_alive=False)
        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        handler.pricing_queue = handler.PricingQueue(FiveZlotyPriceHandler)
        app_dir = os.path.dirname(__file__)
        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.add_to_cart_handler',),
            'TEMPLATE_DIRS': [os.path.join(app_dir, 'templates'),
                              os.path.join(app_dir, '..', 'product',
                                           'tests', 'templates')]
        }
        self.original_settings = self._setup_settings(self.custom_settings)

    def tearDown(self):
        handler.pricing_queue = handler.PricingQueue(*self.original_handlers)
        self._teardown_settings(self.original_settings,
                                self.custom_settings)

    def test_order_is_updated_when_cart_content_changes(self):
        cart = cart_app.Cart.objects.create(typ='satchless.test_cart')
        cart.replace_item(self.macaw_blue, 1)

        order = order_app.Order.objects.get_from_cart(cart)

        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant',
                                                       'quantity'))
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

    def test_order_view(self):
        cart = cart_app.Cart.objects.create(typ='satchless.test_cart')
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        order = order_app.Order.objects.get_from_cart(cart)
        self._test_GET_status(order_app.reverse('details',
                                                args=(order.token,)))

    def test_order_index_view(self):
        username, password = 'foo', 'password'
        User.objects.create_user(username=username, password=password,
                                 email='test@example.com')
        self.authorized_client = Client()
        self.authorized_client.login(username=username,
                                     password=password)
        self._test_GET_status(order_app.reverse('index'),
                              client_instance=self.authorized_client)
