# -*- coding: utf-8 -*-
from decimal import Decimal
import os

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.models import User
from django.test import Client
from prices import Price

from . import models
from .app import MagicOrderApp
from ..checkout.app import CheckoutApp
from ..cart.tests import cart_app
from ..product.tests import DeadParrot
from ..util.models import construct
from ..util.tests import ViewsTestCase


class TestOrder(construct(models.Order, cart=cart_app.Cart)):
    pass


class TestDeliveryGroup(construct(models.DeliveryGroup,
                                  order=TestOrder)):
    pass


class TestOrderedItem(construct(models.OrderedItem,
                                delivery_group=TestDeliveryGroup,
                                variant=cart_app.product_app.Variant)):
    pass


class TestOrderApp(MagicOrderApp):

    Order = TestOrder
    DeliveryGroup = TestDeliveryGroup
    OrderedItem = TestOrderedItem

order_app = TestOrderApp(cart_app=cart_app)


class TestCheckoutApp(CheckoutApp):

    Order = order_app.Order
    Cart = cart_app.Cart

checkout_app = TestCheckoutApp(cart_app=cart_app)


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
        app_dir = os.path.dirname(__file__)
        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.add_to_cart_handler',),
            'TEMPLATE_DIRS': [os.path.join(app_dir, 'templates'),
                              os.path.join(app_dir, '..', 'product',
                                           'tests', 'templates')]
        }
        self.original_settings = self._setup_settings(self.custom_settings)

    def tearDown(self):
        self._teardown_settings(self.original_settings,
                                self.custom_settings)

    def test_order_has_proper_total(self):
        cart = cart_app.Cart.objects.create()
        cart.replace_item(self.macaw_blue, 1)

        order = checkout_app.Order.objects.create(cart=cart, user=cart.owner)
        checkout_app.partition_cart(cart, order)
        self.assertEquals(
            order.get_total(),
            Price(5, currency=settings.SATCHLESS_DEFAULT_CURRENCY))

    def test_order_get_delivery_price(self):
        """Order.get_delivery_price returns a Price object"""

        cart = cart_app.Cart.objects.create()
        cart.replace_item(self.macaw_blue, 1)

        order = checkout_app.Order.objects.create(cart=cart, user=cart.owner)
        checkout_app.partition_cart(cart, order)
        self.assertEquals(
            order.get_delivery_price(),
            Price(0, currency=settings.SATCHLESS_DEFAULT_CURRENCY))

    def test_order_content_is_deleted_when_cart_content_changes(self):
        cart = cart_app.Cart.objects.create()
        cart.replace_item(self.macaw_blue, 1)

        order = checkout_app.Order.objects.create(cart=cart, user=cart.owner)
        checkout_app.partition_cart(cart, order)

        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        self.assertTrue(order.is_empty())

    def test_order_view(self):
        cart = cart_app.Cart.objects.create()
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        order = checkout_app.Order.objects.create(cart=cart, user=cart.owner)
        checkout_app.partition_cart(cart, order)
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
