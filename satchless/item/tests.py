from prices import Price, PriceRange
from unittest import TestCase

from ..item import Item, ItemLine, ItemRange, ItemSet


class Swallow(Item):

    def get_price_per_item(self, sale=False):
        if sale:
            return Price(1, currency='USD')
        return Price(5, currency='USD')


class SpanishInquisition(Item):

    def get_price_per_item(self):
        return Price(15, currency='BTC')


class FetchezLaVache(Item):

    def get_price_per_item(self):
        return Price(5, currency='BTC')


class ThingsNobodyExpects(ItemRange):

    def __iter__(self):
        yield SpanishInquisition()
        yield FetchezLaVache()


class SwallowLine(ItemLine):

    def get_quantity(self):
        return 2

    def get_price_per_item(self):
        return Price(5, currency='EUR')


class CoconutLine(ItemLine):

    def get_price_per_item(self):
        return Price(15, currency='EUR')


class ItemTest(TestCase):

    def test_get_price(self):
        'Item.get_price() works'
        swallow = Swallow()
        self.assertEqual(swallow.get_price(), Price(5, currency='USD'))
        self.assertEqual(swallow.get_price(sale=True),
                         Price(1, currency='USD'))


class ItemRangeTest(TestCase):

    def test_get_price_range(self):
        'ItemRange.get_price_range() works and calls its items'
        unexpected = ThingsNobodyExpects()
        self.assertEqual(unexpected.get_price_range(),
                         PriceRange(Price(5, currency='BTC'),
                                    Price(15, currency='BTC')))


class ItemSetTest(TestCase):

    def test_get_total(self):
        'ItemSet.get_total() works and calls its lines'
        coconut_delivery = ItemSet([SwallowLine(), CoconutLine()])
        self.assertEqual(coconut_delivery.get_total(),
                         Price(25, currency='EUR'))

    def test_get_total_on_empty(self):
        'ItemSet.get_total() raises an exception on an empty cart'
        empty = ItemSet()
        self.assertRaises(AttributeError, empty.get_total)
