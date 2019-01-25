from itertools import groupby

from prices import MoneyRange, TaxedMoney, TaxedMoneyRange

__all__ = ['ClassifyingPartitioner', 'InsufficientStock', 'Item',
           'ItemLine', 'ItemRange', 'ItemSet', 'Partitioner', 'StockedItem',
           'partition']


class InsufficientStock(Exception):

    def __init__(self, item):
        super(InsufficientStock, self).__init__(
            'Insufficient stock for %r' % (item,))
        self.item = item


class ItemRange:
    """
    Represents a group of products like a product with multiple variants
    """
    def __iter__(self):
        raise NotImplementedError()

    def get_price_per_item(self, item, **kwargs):
        return item.get_price(**kwargs)

    def get_price_range(self, **kwargs):
        prices = [self.get_price_per_item(item, **kwargs) for item in self]
        if not prices:
            raise AttributeError(
                'Calling get_price_range() on an empty item range')

        lowest_price = min(prices)
        highest_price = max(prices)

        if type(lowest_price) != type(highest_price):
            raise AttributeError(
                'Cannot get_price_range() on an item range with different price types')

        if isinstance(lowest_price, TaxedMoney):
            return TaxedMoneyRange(lowest_price, highest_price)
        else:
            return MoneyRange(lowest_price, highest_price)


class ItemSet:
    """
    Represents a set of products like an order or a basket
    """
    def __iter__(self):
        raise NotImplementedError()

    def get_subtotal(self, item, **kwargs):
        return item.get_total(**kwargs)

    def get_total(self, **kwargs):
        subtotals = [self.get_subtotal(item, **kwargs) for item in self]
        if not subtotals:
            raise AttributeError('Calling get_total() on an empty item set')
        return sum(subtotals[1:], subtotals[0])


class ItemList(list, ItemSet):

    def __repr__(self):
        return 'ItemList(%s)' % (super(ItemList, self).__repr__(),)


class ItemLine:
    """
    Represents a single line of an order or basket
    """
    def get_price_per_item(self, **kwargs):
        raise NotImplementedError()

    def get_quantity(self, **kwargs):
        return 1

    def get_total(self, **kwargs):
        """
        Override to apply rounding
        """
        return self.get_price_per_item(**kwargs) * self.get_quantity(**kwargs)


class Item:
    """
    Stands for a single product or a single product variant (ie. White XL
    shirt)
    """
    def get_price_per_item(self, **kwargs):
        raise NotImplementedError()

    def get_price(self, **kwargs):
        return self.get_price_per_item(**kwargs)


class Partitioner(ItemSet):
    """
    Represents an ItemSet partitioned for purposes such as delivery

    Override the __iter__() method to provide custom partitioning.
    """
    def __init__(self, subject):
        self.subject = subject

    def __iter__(self):
        'Override this method to provide custom partitioning'
        yield ItemList(list(self.subject))

    def __bool__(self):
        return bool(self.subject)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.subject)


class ClassifyingPartitioner(Partitioner):

    def __iter__(self):
        subject = sorted(self.subject, key=self.classify)
        for classifier, items in groupby(subject, key=self.classify):
            yield self.get_partition(classifier, items)

    def classify(self, item):
        raise NotImplementedError()

    def get_partition(self, classifier, items):
        return ItemList(items)


class GroupingPartitioner(ClassifyingPartitioner):

    def __init__(self, subject, keyfunc, partition_class):
        self.keyfunc = keyfunc
        self.partition_class = partition_class
        super(GroupingPartitioner, self).__init__(subject)

    def classify(self, item):
        return self.keyfunc(item)

    def get_partition(self, classifier, items):
        return self.partition_class(items)


def partition(subject, keyfunc, partition_class=ItemList):
    return GroupingPartitioner(subject, keyfunc, partition_class)


class StockedItem(Item):

    def get_stock(self):
        raise NotImplementedError()

    def check_quantity(self, quantity):
        if quantity < 0:
            raise ValueError('Negative quantities are not supported')
        if quantity > self.get_stock():
            raise InsufficientStock(self)
