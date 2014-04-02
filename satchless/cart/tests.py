from prices import Price
from unittest import TestCase

from . import Cart, CartLine
from ..item import InsufficientStock, Item, StockedItem


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


class LimitedShrubbery(StockedItem):

    def get_stock(self):
        return 1


class CartLineTest(TestCase):

    def test_getstate(self):
        'CartLine.__getstate__() returns a tuple of all values'
        cart_line = CartLine('shrubbery', 0)
        state = cart_line.__getstate__()
        self.assertEqual(state, ('shrubbery', 0, None))

    def test_setstate(self):
        'CartLine.__setstate__() properly restores all fields'
        cart_line = CartLine('apple', 2, 'jonagold')
        cart_line.__setstate__(('shrubbery', 1, 'trimmed'))
        self.assertEqual(cart_line.product, 'shrubbery')
        self.assertEqual(cart_line.quantity, 1)
        self.assertEqual(cart_line.data, 'trimmed')

    def test_equality(self):
        'Cart lines are only equal to cart lines with equal attributes'
        apple = CartLine('apple', 1, None)
        self.assertEqual(apple, CartLine('apple', 1, None))
        orange = CartLine('orange', 1, None)
        self.assertNotEqual(apple, orange)
        self.assertNotEqual(apple, 5)

    def test_repr(self):
        'CartLine.__repr__() returns valid code'
        shrubbery = CartLine('shrubbery', 1, None)
        self.assertEqual(
            repr(shrubbery),
            "CartLine(product='shrubbery', quantity=1, data=None)")

    def test_get_total(self):
        'CartLine.get_total() works and correctly passes **kwargs'
        swallows_a = CartLine(Swallow(kind='african'), 2, None)
        self.assertEqual(swallows_a.get_total(), Price(20, currency='BTC'))
        swallows_e = CartLine(Swallow(kind='european'), 2, None)
        self.assertEqual(swallows_e.get_total(), Price(20, currency='GBP'))


class CartTest(TestCase):

    def test_add_zero_does_nothing(self):
        'Zero quantity is not stored in the cart'
        cart = Cart()
        cart.add('shrubbery', 0)
        self.assertEqual(cart.count(), 0)
        self.assertEqual(list(cart), [])

    def test_add_increases_count(self):
        'Cart.add() increases previous quantity'
        cart = Cart()
        cart.add('shrubbery')
        self.assertEqual(cart.count(), 1)
        cart.add('shrubbery', 2)
        self.assertEqual(cart.count(), 3)

    def test_negative_add_allowed(self):
        'Negative values are allowed as long as the result is not negative'
        cart = Cart()
        cart.add('swallow', 3)
        cart.add('swallow', -1)
        self.assertEqual(cart.count(), 2)

    def test_negative_shalt_thou_not_count(self):
        'No operation can result in negative quantity'
        cart = Cart()
        self.assertRaises(ValueError,
                          lambda: cart.add('holy hand grenade', -1, None))

    def test_bad_values_do_not_break_state(self):
        'Invalid operations do not alter the cart state'
        cart = Cart()
        cart.add('seconds', 3)
        self.assertRaises(TypeError, lambda: cart.add('seconds', 'five'))
        self.assertEqual(cart[0], CartLine('seconds', 3))

    def test_replace(self):
        'Cart.add(replace=True) replaces existing quantity'
        cart = Cart()
        cart.add('shrubbery')
        self.assertEqual(cart.count(), 1)
        cart.add('shrubbery', 10, replace=True)
        self.assertEqual(cart.count(), 10)

    def test_replace_by_zero(self):
        'Replacing by zero quantity removes the item from cart'
        cart = Cart()
        cart.add('shrubbery')
        self.assertEqual(cart.count(), 1)
        cart.add('shrubbery', 0, replace=True)
        self.assertEqual(cart.count(), 0)

    def test_data_is_stored(self):
        'Data is stored in cart lines'
        cart = Cart()
        cart.add('shrubbery', 10, data='trimmed')
        self.assertEqual(list(cart), [CartLine('shrubbery', 10, 'trimmed')])

    def test_data_uniqueness(self):
        'Unique data results in a separate cart line'
        cart = Cart()
        cart.add('shrubbery', 10)
        cart.add('shrubbery', 10, data='trimmed', replace=True)
        self.assertEqual(cart.count(), 20)

    def test_getstate(self):
        'Cart.__getstate__() returns a list of cart lines'
        cart = Cart()
        state = cart.__getstate__()
        self.assertEqual(state, ([],))
        cart.add('shrubbery', 2)
        state = cart.__getstate__()
        self.assertEqual(state, ([CartLine('shrubbery', 2, None)],))

    def test_getstate_is_true(self):
        'Cart.__getstate__() returns a truthy value'
        cart = Cart()
        state = cart.__getstate__()
        self.assertTrue(state)

    def test_setstate(self):
        'Cart.__setstate__() properly restores state'
        cart = Cart()
        cart.__setstate__(([CartLine('shrubbery', 2, None)],))
        self.assertEqual(cart._state, [CartLine('shrubbery', 2, None)])

    def test_setstate_resets_modified(self):
        'Cart.__setstate__() sets modified to False'
        cart = Cart()
        cart.modified = True
        cart.__setstate__(([],))
        self.assertFalse(cart.modified)

    def test_init_with_items(self):
        'Passing lines to Cart.__init__() works'
        carrier = CartLine('swallow', 2, 'african')
        payload = CartLine('coconut', 1, None)
        cart = Cart([carrier, payload])
        self.assertEqual(cart.count(), 3)

    def test_repr(self):
        'Cart.__repr__() returns valid code'
        cart = Cart()
        cart.add('rabbit')
        self.assertEqual(
            repr(cart),
            "Cart([CartLine(product='rabbit', quantity=1, data=None)])")

    def test_truthiness(self):
        'bool(cart) is only true if cart contains items'
        cart = Cart()
        self.assertFalse(cart)
        cart.add('book of armaments')
        self.assertTrue(cart)

    def test_sufficient_quantity(self):
        'Cart.add() should allow product to be added if enough is in stock'
        cart = Cart()
        cart.add(LimitedShrubbery(), 1)

    def test_insufficient_quantity(self):
        'Cart.add() should disallow product to be added if stock is exceeded'
        cart = Cart()
        self.assertRaises(InsufficientStock,
                          lambda: cart.add(LimitedShrubbery(), 2))

    def test_insufficient_quantity_without_checks(self):
        'Cart.add() should allow product to exceeded stock with checks off'
        cart = Cart()
        cart.add(LimitedShrubbery(), 2, check_quantity=False)
        self.assertEqual(cart[0].quantity, 2)

    def test_clear(self):
        'Cart.clear() clears the cart and marks it as modified'
        cart = Cart()
        cart.add('rabbit')
        cart.modified = False
        cart.clear()
        self.assertEqual(len(cart), 0)
        self.assertEqual(cart.modified, True)

