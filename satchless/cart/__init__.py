from satchless.item import ItemSet, ItemLine


class CartLine(ItemLine):

    def __init__(self, product, quantity, data=None):
        self.product = product
        self._quantity = quantity
        self.data = data

    def __repr__(self):
        return 'CartLine(product=%r, quantity=%r, data=%r)' % (
            self.product, self.quantity, self.data)

    def get_quantity(self):
        return self._quantity

    quantity = property(get_quantity)

    def get_price_per_item(self, **kwargs):
        return self.product.get_price(**kwargs)


class Cart(ItemSet):

    SESSION_KEY = 'cart'
    modified = False

    state = None

    def __init__(self, items=None):
        self.state = {}
        self.modified = True
        items = items or []
        for l in items:
            self.add_item(l.product, l.quantity, l.data, replace=True)

    def __repr__(self):
        return 'Cart(%r)' % (list(self),)

    def __iter__(self):
        for key, qty in self.state.iteritems():
            product, data = key
            yield CartLine(product, qty, data)

    def __getstate__(self):
        return self.state

    def __setstate__(self, state):
        self.state = state

    def count(self):
        return sum([item.get_quantity() for item in self])

    def check_quantity(self, product, quantity, data=None):
        return True

    def add_item(self, product, quantity, data=None, replace=False):
        key = (product, data)
        if not replace and key in self.state:
            quantity += self.state[key]

        if quantity < 0:
            raise ValueError('%r is not a valid quantity' % (quantity,))

        self.check_quantity(product, quantity, data)

        if not quantity and product in self:
            del self.state[key]
        elif quantity:
            self.state[key] = quantity

        self.modified = True
