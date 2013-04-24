from prices import Price, PriceRange
from unittest import TestCase

from . import Item, ItemLine, ItemRange, Partitioner, ItemList


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


class EmptyRange(ItemRange):

    def __iter__(self):
        return iter([])


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

    def test_get_price_range_on_empty(self):
        'ItemRange.get_price_range() raises an exception on an empty range'
        empty = EmptyRange()
        self.assertRaises(AttributeError, empty.get_price_range)


class ItemListTest(TestCase):

    def test_repr(self):
        'ItemList.__repr__() returns valid code'
        item_list = ItemList([1])
        self.assertEqual(item_list.__repr__(), 'ItemList([1])')

    def test_get_total(self):
        'ItemSet.get_total() works and calls its lines'
        coconut_delivery = ItemList([SwallowLine(), CoconutLine()])
        self.assertEqual(coconut_delivery.get_total(),
                         Price(25, currency='EUR'))

    def test_get_total_on_empty(self):
        'ItemSet.get_total() raises an exception on an empty cart'
        empty = ItemList()
        self.assertRaises(AttributeError, empty.get_total)


class PartitionerTest(TestCase):

    def test_default_is_all_items(self):
        'Default implementation returns a single group with all items'
        fake_cart = ['one', 'two', 'five']
        partitioner = Partitioner(fake_cart)
        self.assertEqual(list(partitioner), [ItemList(fake_cart)])

    def test_total_works(self):
        'Partitioner returns the same price the cart does'
        item_set = ItemList([SwallowLine()])
        partitioner = Partitioner(item_set)
        self.assertEqual(partitioner.get_total(), Price(10, currency='EUR'))

    def test_truthiness(self):
        'bool(partitioner) is only true if the set contains items'
        item_set = ItemList()
        partitioner = Partitioner(item_set)
        self.assertFalse(partitioner)
        item_set = ItemList([SwallowLine()])
        partitioner = Partitioner(item_set)
        self.assertTrue(partitioner)
