from prices import Price
from django.test import TestCase
from satchless.item import ItemLine

from ...cart import Cart
from ...product.tests import product_app
from ...util.models import construct
from .. import models

class Product(ItemLine):

    def get_price_per_item(self, **kwargs):
        return Price(1)

class TestSessionCart(TestCase):

    def setUp(self):
        self.cart = Cart()
        self.product = Product()

    def test_add_item(self):
        cart_item = self.cart.add_item(self.product, 0)
        self.assertIsNone(cart_item)
        cart_item = self.cart.add_item(self.product, 1)
        self.assertEqual(cart_item.get_quantity(), 1)
        cart_item = self.cart.add_item(self.product, 2)
        self.assertEqual(cart_item.get_quantity(), 3)

        self.assertEqual((len(self.cart)), 3)

    def test_replace_item(self):
        cart_item = self.cart.replace_item(self.product, 10)
        self.assertEqual(cart_item.get_quantity(), 10)

        self.assertEqual((len(self.cart)), 10)

    def test_check_quantity(self):

        quantity = self.cart.check_quantity(self.product, 3)
        self.assertEqual(quantity, 3)

        quantity = self.cart.check_quantity(self.product, 0, replace=True)
        self.assertEqual(quantity, 0)

        quantity = self.cart.check_quantity(self.product, -3, replace=True)
        self.assertEqual(quantity, 0)

        self.assertEqual((len(self.cart)), 0)


class TestCart(models.Cart):
    pass


class TestCartItem(construct(models.CartItem, cart=TestCart,
                             variant=product_app.Variant)):
    pass

from .app import AppTestCase
from .magic_app import MagicAppTestCase, cart_app
from .models import ModelsTestCase

__all__ = ['AppTestCase', 'cart_app', 'MagicAppTestCase', 'ModelsTestCase',
           'CartTest']
