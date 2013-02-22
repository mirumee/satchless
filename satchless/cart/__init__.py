from decimal import Decimal
from django.conf import settings
from django.utils.translation import ugettext as _
from satchless.item import ItemSet, ItemLine


class CartItem(ItemLine):

    def __init__(self, product, quantity):
        self._product = product
        self._quantity = quantity

    def get_product(self):
        return self._product

    def get_quantity(self):
        return self._quantity

    def get_price_per_item(self, **kwargs):
        return self._product.get_price(**kwargs)


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
        return sum([item.get_quantity() for item in self])

    def __unicode__(self):
        return _('Cart (%(cart_count)s)' % {'cart_count': len(self)})

    def check_quantity(self, product, quantity, data=None):
        return True

    def add_item(self, product, quantity, data=None, replace=False):
        if not replace and product in self:
            quantity += self[product].get_quantity()

        if quantity < 0:
            raise ValueError('%r is not a valid quantity' % (quantity,))

        self.check_quantity(product, quantity, data)

        if not quantity and product in self:
            del self[product]
        elif quantity:
            self[product] = quantity
            return self[product]

