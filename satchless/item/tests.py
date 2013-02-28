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


class ListBasedSet(list, ItemSet):
    pass


class ItemTest(TestCase):

    def test_get_price(self):
        swallow = Swallow()
        self.assertEqual(swallow.get_price(), Price(5, currency='USD'))
        self.assertEqual(swallow.get_price(sale=True),
                         Price(1, currency='USD'))


class ItemRangeTest(TestCase):

    def test_get_price_range(self):
        unexpected = ThingsNobodyExpects()
        self.assertEqual(unexpected.get_price_range(),
                         PriceRange(Price(5, currency='BTC'),
                                    Price(15, currency='BTC')))


class ItemSetTest(TestCase):
    
    def test_get_total(self):
        coconut_delivery = ListBasedSet([SwallowLine(), CoconutLine()])
        self.assertEqual(coconut_delivery.get_total(),
                         Price(25, currency='EUR'))

    def test_get_total_on_empty(self):
        empty = ListBasedSet()
        self.assertEqual(empty.get_total(), None)
