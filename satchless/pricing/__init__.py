from decimal import Decimal


class Price(object):
    gross = Decimal('NaN')
    net = Decimal('NaN')
    currency = None
    tax_name = None

    def __init__(self, net=None, gross=None, currency=None, tax_name=''):
        if net is not None:
            self.net = Decimal(net)
        if gross is None:
            self.gross = self.net
        else:
            self.gross = Decimal(gross)
        self.currency = currency
        self.tax_name = tax_name

    def __repr__(self):
        return ("Price(net=%s, gross=%s, currency=%s)" %
                (repr(self.net), repr(self.gross), repr(self.currency)))

    def __cmp__(self, other):
        if not isinstance(other, Price):
            raise TypeError('Cannot compare Price to %s' % other)
        if self.currency != other.currency:
            raise ValueError('Cannot compare Prices in %s and %s' %
                             (self.currency, other.currency))
        if self.net < other.net:
            return -1
        elif self.net > other.net:
            return 1
        return 0

    def __eq__(self, other):
        if isinstance(other, Price):
            return (self.gross == other.gross and
                    self.net == other.net and
                    self.currency == other.currency)
        return False

    def __ne__(self, other):
        return not self == other

    def __mul__(self, other):
        price_net = self.net * other
        price_gross = self.gross * other
        return Price(net=price_net, gross=price_gross, currency=self.currency,
                     tax_name=self.tax_name)

    def __add__(self, other):
        if isinstance(other, Tax):
            return other.apply(self)
        if not isinstance(other, Price):
            raise TypeError("Cannot add %s object to Price" % type(other))
        if other.currency != self.currency:
            raise ValueError("Cannot add Price in %s to %s" % (self.currency,
                                                               other.currency))
        price_net = self.net + other.net
        price_gross = self.gross + other.gross
        if self.tax_name == other.tax_name:
            return Price(net=price_net, gross=price_gross,
                         currency=self.currency, tax_name=self.tax_name)
        return Price(net=price_net, gross=price_gross, currency=self.currency)

    def has_value(self):
        return not (self.net.is_nan() and self.gross.is_nan())

    @property
    def tax(self):
        return self.gross - self.net


class PriceRange(object):
    min_price = None
    max_price = None

    def __init__(self, min_price, max_price=None):
        self.min_price = min_price
        if max_price is None:
            max_price = min_price
        if min_price > max_price:
            raise ValueError('Cannot create a PriceRange from %s to %s' %
                             (min_price, max_price))
        if min_price.currency != max_price.currency:
            raise ValueError('Cannot create a PriceRange as %s and %s use'
                             ' different currencies' % (min_price, max_price))
        self.max_price = max_price

    def __repr__(self):
        return ("PriceRange(%s, %s)" %
                (repr(self.min_price), repr(self.max_price)))

    def __add__(self, other):
        if isinstance(other, Tax):
            return PriceRange(min_price=other.apply(self.min_price),
                              max_price=other.apply(self.max_price))
        if not isinstance(other, (Price, PriceRange)):
            raise TypeError("Cannot add %s object to PriceRange" % type(other))
        if isinstance(other, Price):
            if other.currency != self.min_price.currency:
                raise ValueError("Cannot add PriceRange in %s to Price in %s" %
                                 (self.min_price.currency, other.currency))
            min_price = self.min_price + other
            max_price = self.max_price + other
            return PriceRange(min_price=min_price, max_price=max_price)
        else:
            if other.min_price.currency != self.min_price.currency:
                raise ValueError("Cannot add PriceRanges in %s and %s" %
                                 (self.min_price.currency,
                                  other.min_price.currency))
            min_price = self.min_price + other.min_price
            max_price = self.max_price + other.max_price
            return PriceRange(min_price=min_price, max_price=max_price)

    def __eq__(self, other):
        if isinstance(other, PriceRange):
            return (self.min_price == other.min_price and
                    self.max_price == other.max_price)
        return False

    def __ne__(self, other):
        return not self == other

    def __contains__(self, item):
        if not isinstance(item, Price):
            raise TypeError('PriceRange cannot contain %s object' % item)
        return self.min_price <= item <= self.max_price

    def replace(self, min_price=None, max_price=None):
        '''
        Return a new PriceRange object with one or more properties set to
        values passed to this method.
        '''
        if min_price is None:
            min_price = self.min_price
        if max_price is None:
            max_price = self.max_price
        return PriceRange(min_price=min_price, max_price=max_price)


class Tax(object):
    name = None

    def apply(self, price):
        raise NotImplementedError()


class LinearTax(Tax):
    def __init__(self, multiplier, name=None):
        self.multiplier = multiplier
        self.name = name or self.name

    def apply(self, price):
        return Price(net=price.net,
                     gross=price.gross * self.multiplier,
                     currency=price.currency,
                     tax_name=self.name)


class PricingHandler(object):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        raise NotImplementedError()

    def get_product_price_range(self, product, currency, **kwargs):
        raise NotImplementedError()

    def get_items_prices(self, items):
        '''
        DO NOT OVERRIDE THIS METHOD unless you know exactly what you are doing!

        This is to ensure correct types for iterative computing prices by
        many handlers.

        If you are adding method for updating prices, e.g. some kind of discount
        override compute_new_prices.
        '''
        try:
            updated_prices = self.compute_new_prices(items)
        except NotImplemented:
            return items
        assert len(updated_prices) == len(items), \
            "Price list must be of the same length as item list"
        return [(variant, cnt, price)
                for ((variant, cnt, _), price)
                in zip(items, updated_prices)]

    def compute_new_prices(self, items):
        '''
        This is method for updating prices in item collection.

        items is list of tuples: (variant, quantity, price)

        Resulting value needs to be list of updated prices.

        Basic implementation could look like:
        return [price * quantity for (variant, quantity, price) in items]
        '''
        raise NotImplemented


class StopPropagation(Exception):
    pass
