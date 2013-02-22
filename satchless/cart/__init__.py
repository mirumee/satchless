from decimal import Decimal
from django.conf import settings
from django.utils.translation import ugettext as _
from satchless.item import ItemSet, ItemLine


class InvalidQuantityException(Exception):

    def __init__(self, reason, quantity_delta):
        self.reason = reason
        self.quantity_delta = quantity_delta

    def __str__(self):
        return self.reason


class CartItem(ItemLine):

    def __init__(self, product, quantity):
        self._product = product
        self._quantity = quantity

    def _get_product(self):
        return self._product

    def get_quantity(self):
        return self._quantity

    def get_price_per_item(self):
        return self._product.price

    product = property(_get_product)
    quantity = property(get_quantity)


class Cart(dict, ItemSet):

    SESSION_KEY = 'cart'
    modified = False

    def __iter__(self):
        for product, quantity in self.items():
            yield CartItem(product, quantity)

    def __getitem__(self, key):
        return CartItem(key, super(Cart, self).__getitem__(key))

    def __setitem__(self, key, val):
        self.modified = True
        return dict.__setitem__(self, key, val)

    def __len__(self):
        return sum([item.quantity for item in self])

    def __unicode__(self):
        return _('Cart (%(cart_count)s)' % {'cart_count': len(self)})

    def check_quantity(self, product, quantity, replace=False):
        '''
        Method checks quantity value. Return valid quantity or raise
        InvalidQuantityException.
        '''
        if not replace and product in self:
            quantity += self[product].get_quantity()

        if quantity < 0:
            quantity = Decimal(0)

        return quantity

    def add_item(self, product, quantity, replace=False):
        quantity = self.check_quantity(product, quantity, replace=replace)

        if not quantity and product in self:
            del self[product]
        elif quantity:
            self[product] = quantity
            return self[product]

    def replace_item(self, product, quantity):
        return self.add_item(product, quantity, replace=True)

    def get_default_currency(self, **kwargs):
        return settings.SATCHLESS_DEFAULT_CURRENCY

