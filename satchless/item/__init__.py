from prices import PriceRange

__all__ = ('Item', 'ItemLine', 'ItemRange', 'ItemSet')


class ItemRange(object):
    """
    Represents a group of products like a product with multiple variants
    """
    def __iter__(self):
        raise NotImplementedError  # pragma: no cover

    def get_price_per_item(self, item, **kwargs):
        return item.get_price(**kwargs)

    def get_price_range(self, **kwargs):
        prices = [self.get_price_per_item(item, **kwargs) for item in self]
        if not prices:
            raise AttributeError(
                'Calling get_price_range() on an empty item range')
        return PriceRange(min(prices), max(prices))


class ItemSet(object):
    """
    Represents a set of products like an order or a basket
    """
    def __iter__(self):
        raise NotImplementedError  # pragma: no cover

    def get_subtotal(self, item, **kwargs):
        return item.get_total(**kwargs)

    def get_total(self, **kwargs):
        subtotals = [self.get_subtotal(item, **kwargs) for item in self]
        if not subtotals:
            raise AttributeError('Calling get_total() on an empty item set')
        return sum(subtotals[1:], subtotals[0])


class ItemList(list, ItemSet):
    pass


class ItemLine(object):
    """
    Represents a single line of an order or basket
    """
    def get_price_per_item(self, **kwargs):
        return NotImplemented  # pragma: no cover

    def get_quantity(self, **kwargs):
        return 1

    def get_total(self, **kwargs):
        """
        Override to apply rounding
        """
        return self.get_price_per_item(**kwargs) * self.get_quantity(**kwargs)


class Item(object):
    """
    Stands for a single product or a single product variant (ie. White XL shirt)
    """
    def get_price_per_item(self, **kwargs):
        return NotImplemented  # pragma: no cover

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

    def __nonzero__(self):
        return bool(self.subject)
