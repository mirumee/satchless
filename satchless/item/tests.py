from prices import Money, MoneyRange, TaxedMoney, TaxedMoneyRange
from unittest import TestCase

from . import (ClassifyingPartitioner, InsufficientStock, Item, ItemLine,
               ItemList, ItemRange, Partitioner, StockedItem, partition)


class Swallow(Item):

    def get_price_per_item(self, sale=False):
        if sale:
            return Money(1, currency='USD')
        return Money(5, currency='USD')


class Robin(Item):

    def get_price_per_item(self):
        return TaxedMoney(Money(8, currency='USD'), Money(10, currency='USD'))


class RareRobin(Item):
    def get_price_per_item(self):
        return TaxedMoney(Money(12, currency='USD'), Money(15, currency='USD'))


class SpanishInquisition(Item):

    def get_price_per_item(self):
        return Money(15, currency='BTC')


class FetchezLaVache(Item):

    def get_price_per_item(self):
        return Money(5, currency='BTC')


class EmptyRange(ItemRange):

    def __iter__(self):
        return iter([])


class ThingsNobodyExpects(ItemRange):

    def __iter__(self):
        yield SpanishInquisition()
        yield FetchezLaVache()


class TaxedThings(ItemRange):

    def __iter__(self):
        yield Robin()
        yield RareRobin()


class SwallowLine(ItemLine):

    def get_quantity(self):
        return 2

    def get_price_per_item(self):
        return Money(5, currency='EUR')


class CoconutLine(ItemLine):

    def get_price_per_item(self):
        return Money(15, currency='EUR')


class LimitedShrubbery(StockedItem):

    def get_stock(self):
        return 1


class SwallowPartitioner(ClassifyingPartitioner):

    def classify(self, item):
        if isinstance(item, Swallow):
            return 'swallow'
        return 'unknown'


class ItemTest(TestCase):

    def test_get_price(self):
        'Item.get_price() works'
        swallow = Swallow()
        self.assertEqual(swallow.get_price(), Money(5, currency='USD'))
        self.assertEqual(swallow.get_price(sale=True),
                         Money(1, currency='USD'))

        robin = Robin()
        self.assertEqual(robin.get_price(), TaxedMoney(
                         Money(8, currency='USD'), Money(10, currency='USD')))


class ItemRangeTest(TestCase):

    def test_get_price_range(self):
        'ItemRange.get_price_range() works and calls its items'
        unexpected = ThingsNobodyExpects()
        self.assertEqual(unexpected.get_price_range(),
                         MoneyRange(Money(5, currency='BTC'),
                                    Money(15, currency='BTC')))

        taxed = TaxedThings()
        self.assertEqual(taxed.get_price_range(),
                         TaxedMoneyRange(
                            TaxedMoney(Money(8, currency='USD'), Money(10, currency='USD')),
                            TaxedMoney(Money(12, currency='USD'), Money(15, currency='USD'))))

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
                         Money(25, currency='EUR'))

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
        self.assertEqual(partitioner.get_total(), Money(10, currency='EUR'))

    def test_truthiness(self):
        'bool(partitioner) is only true if the set contains items'
        item_set = ItemList()
        partitioner = Partitioner(item_set)
        self.assertFalse(partitioner)
        item_set = ItemList([SwallowLine()])
        partitioner = Partitioner(item_set)
        self.assertTrue(partitioner)

    def test_repr(self):
        'Partitioner.__repr__() returns valid code'
        partitioner = Partitioner([1])
        self.assertEqual(partitioner.__repr__(), 'Partitioner([1])')


class ClassifyingPartitionerTest(TestCase):

    def test_classification(self):
        'Partitions should be split according to the classifying key'
        swallow = Swallow()
        inquisition = SpanishInquisition()
        cow = FetchezLaVache()
        fake_cart = [inquisition, swallow, cow]
        partitioner = SwallowPartitioner(fake_cart)
        self.assertEqual(list(partitioner),
                         [ItemList([swallow]),
                          ItemList([inquisition, cow])])


class PartitionTest(TestCase):

    def test_basic_classification(self):
        def keyfunc(item):
            if item > 5:
                return 'more'
            return 'less'
        partitioner = partition([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], keyfunc)
        self.assertEqual(list(partitioner),
                         [ItemList([1, 2, 3, 4, 5]),
                          ItemList([6, 7, 8, 9, 10])])

    def test_custom_class(self):
        def keyfunc(item):
            if item > 5:
                return 'more'
            return 'less'
        partitioner = partition([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], keyfunc,
                                partition_class=list)
        self.assertEqual(list(partitioner),
                         [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])


class StockedItemTest(TestCase):

    def test_check_valid_quantity(self):
        'StockedItem.get_quantity() allows smaller quantities to be used'
        item = LimitedShrubbery()
        item.check_quantity(0)
        item.check_quantity(1)

    def test_check_negative_quantity(self):
        'StockedItem.get_quantity() disallows negative quantities'
        item = LimitedShrubbery()
        self.assertRaises(ValueError, lambda: item.check_quantity(-1))

    def test_check_excessive_quantity(self):
        'StockedItem.get_quantity() disallows excessive quantities'
        item = LimitedShrubbery()
        self.assertRaises(InsufficientStock, lambda: item.check_quantity(2))
