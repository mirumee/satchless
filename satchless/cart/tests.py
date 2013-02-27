from prices import Price
from unittest import TestCase

from . import Cart, CartLine
from ..item import ItemLine


class TestCartLine(TestCase):

    def test_getstate(self):
        cart_line = CartLine('shrubbery', 0)
        state = cart_line.__getstate__()

        self.assertEqual(state, ('shrubbery', 0, None))

    def test_setstate(self):
        cart_line = CartLine('apple', 2, 'jonagold')
        cart_line.__setstate__(('shrubbery', 1, 'trimmed'))

        self.assertEqual('shrubbery', cart_line.product)
        self.assertEqual(1, cart_line.get_quantity())
        self.assertEqual('trimmed', cart_line.data)


class TestCart(TestCase):

    def test_empty_add_does_nothing(self):
        cart = Cart()
        cart.add_line('shrubbery', 0)
        self.assertEqual(cart.count(), 0)
        self.assertEqual(list(cart), [])

    def test_add_increases_count(self):
        cart = Cart()
        cart.add_line('shrubbery', 1)
        self.assertEqual(cart.count(), 1)
        cart.add_line('shrubbery', 2)
        self.assertEqual(cart.count(), 3)

    def test_replace(self):
        cart = Cart()
        cart.add_line('shrubbery', 1)
        self.assertEqual(cart.count(), 1)
        cart.add_line('shrubbery', 10, replace=True)
        self.assertEqual(cart.count(), 10)

    def test_replace_by_zero(self):
        cart = Cart()
        cart.add_line('shrubbery', 1)
        self.assertEqual(cart.count(), 1)
        cart.add_line('shrubbery', 0, replace=True)
        self.assertEqual(cart.count(), 0)

    def test_data_uniqueness(self):
        cart = Cart()
        cart.add_line('shrubbery', 10)
        cart.add_line('shrubbery', 10, data='trimmed', replace=True)
        self.assertEqual(cart.count(), 20)

    def test_getstate(self):
        cart = Cart()
        state = cart.__getstate__()
        self.assertEqual(cart.state, [])
        cart.add_line('shrubbery', 2)
        self.assertEqual(cart.state, [CartLine('shrubbery', 2, None)])
