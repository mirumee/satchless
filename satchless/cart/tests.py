from prices import Price
from unittest import TestCase

from . import Cart, CartLine
from ..item import ItemLine


class Product(ItemLine):

    def get_price_per_item(self, **kwargs):
        return Price(1)


class TestCartLine(TestCase):

    def test__getstate__(self):
        cart_line = CartLine('shrubbery', 0)
        state = cart_line.__getstate__()

        self.assertEqual(state, ('shrubbery', 0, None))

    def test__setstate__(self):
        cart_line = CartLine('apple', 2, 'jonagold')
        cart_line.__setstate__(('shrubbery', 1, 'trimmed'))

        self.assertEqual('shrubbery', cart_line.product)
        self.assertEqual(1, cart_line.get_quantity())
        self.assertEqual('trimmed', cart_line.data)


class TestCart(TestCase):

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

    def test__getstate__(self):
        cart = Cart()
        state = cart.__getstate__()
        self.assertTrue(isinstance(state, list))
        self.assertEqual(len(cart.state), 0)
        cart.add_line('shrubbery', 2)
        self.assertEqual(len(cart.state), 1)
        self.assertTrue(isinstance(cart.state[0], CartLine))

