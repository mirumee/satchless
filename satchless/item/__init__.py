from prices import Price, PriceRange

__all__ = ('Item', 'ItemLine', 'ItemRange', 'ItemSet')


class ItemRange(object):
    """
    Represents a group of products like a product with multiple variants
    """
    def get_price_per_item(self, item, **kwargs):
        return item.get_price(**kwargs)

    def get_price_range(self, **kwargs):
        prices = [self.get_price_per_item(item, **kwargs) for item in self]
        return PriceRange(min(prices), max(prices))


class ItemSet(object):
    """
    Represents a set of products like an order or a basket
    """
    def get_default_currency(self, **kwargs):
        raise NotImplementedError()

    def get_subtotal(self, line, **kwargs):
        return line.get_total(**kwargs)

    def get_total(self, **kwargs):
        return sum([self.get_subtotal(line, **kwargs) for line in self],
                   Price(0, currency=self.get_default_currency(**kwargs)))


class ItemLine(object):
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


class Item(object):
    """
    Stands for a single product or a single product variant (ie. White XL shirt)
    """
    def get_price_per_item(self, **kwargs):
        raise NotImplementedError()

    def get_price(self, **kwargs):
        return self.get_price_per_item(**kwargs)
