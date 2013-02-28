from prices import Price
from unittest import TestCase

from . import Cart, CartLine
from ..item import Item, ItemLine


class Swallow(Item):

    def __init__(self, kind):
        super(Swallow, self).__init__()
        self.kind = kind

    def get_price_per_item(self):
        if self.kind == 'african':
            return Price(10, currency='BTC')
        elif self.kind == 'european':
            return Price(10, currency='GBP')
        return NotImplemented


class CartLineTest(TestCase):

    def test_getstate(self):
        cart_line = CartLine('shrubbery', 0)
        state = cart_line.__getstate__()
        self.assertEqual(state, ('shrubbery', 0, None))

    def test_setstate(self):
        cart_line = CartLine('apple', 2, 'jonagold')
        cart_line.__setstate__(('shrubbery', 1, 'trimmed'))
        self.assertEqual(cart_line.product, 'shrubbery')
        self.assertEqual(cart_line.quantity, 1)
        self.assertEqual(cart_line.data, 'trimmed')

    def test_equality(self):
        apple = CartLine('apple', 1, None)
        self.assertEqual(apple, CartLine('apple', 1, None))
        orange = CartLine('orange', 1, None)
        self.assertNotEqual(apple, orange)
        self.assertNotEqual(apple, 5)

    def test_repr(self):
        shrubbery = CartLine('shrubbery', 1, None)
        self.assertEqual(
            repr(shrubbery),
            "CartLine(product='shrubbery', quantity=1, data=None)")

    def test_get_total(self):
        swallows_a = CartLine(Swallow(kind='african'), 2, None)
        self.assertEqual(swallows_a.get_total(), Price(20, currency='BTC'))
        swallows_e = CartLine(Swallow(kind='european'), 2, None)
        self.assertEqual(swallows_e.get_total(), Price(20, currency='GBP'))


class CartTest(TestCase):

    def test_add_zero_does_nothing(self):
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

    def test_negative_shalt_thou_not_count(self):
        cart = Cart()
        def illegal():
            cart.add_line('holy hand grenade', -1, None)
        self.assertRaises(ValueError, illegal)

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
        self.assertEqual(state, [])
        cart.add_line('shrubbery', 2)
        state = cart.__getstate__()
        self.assertEqual(state, [CartLine('shrubbery', 2, None)])

    def test_setstate(self):
        cart = Cart()
        state = [CartLine('shrubbery', 2, None)]
        cart.__setstate__(state)
        self.assertEqual(cart.state, [CartLine('shrubbery', 2, None)])

    def test_init_with_items(self):
        carrier = CartLine('swallow', 2, 'african')
        payload = CartLine('coconut', 1, None)
        cart = Cart([carrier, payload])
        self.assertEqual(cart.count(), 3)

    def test_repr(self):
        cart = Cart()
        cart.add_line('rabbit', 1, None)
        self.assertEqual(
            repr(cart),
            "Cart([CartLine(product='rabbit', quantity=1, data=None)])")
