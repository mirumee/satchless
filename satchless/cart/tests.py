from prices import Price
from unittest import TestCase

from . import Cart
from ..item import ItemLine


class Product(ItemLine):

    def get_price_per_item(self, **kwargs):
        return Price(1)


class TestSessionCart(TestCase):

    def test_add_line(self):
        cart = Cart()
        cart.add_line('shrubbery', 0)
        self.assertEqual(cart.count(), 0)
        cart.add_line('shrubbery', 1)
        self.assertEqual(cart.count(), 1)
        cart.add_line('shrubbery', 2)
        self.assertEqual(cart.count(), 3)
        cart.add_line('shrubbery', 10, replace=True)
        self.assertEqual(cart.count(), 10)
        cart.add_line('shrubbery', 10, data='trimmed', replace=True)
        self.assertEqual(cart.count(), 20)

