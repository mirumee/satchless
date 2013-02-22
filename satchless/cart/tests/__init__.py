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

    def test_add_item(self):
        cart = Cart()
        cart.add_item('shrubbery', 0)
        self.assertEqual(cart.count(), 0)
        cart.add_item('shrubbery', 1)
        self.assertEqual(cart.count(), 1)
        cart.add_item('shrubbery', 2)
        self.assertEqual(cart.count(), 3)
        cart.add_item('shrubbery', 10, replace=True)
        self.assertEqual(cart.count(), 10)
        cart.add_item('shrubbery', 10, data='trimmed', replace=True)
        self.assertEqual(cart.count(), 20)


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
