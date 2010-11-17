from decimal import Decimal
from django.conf import settings
from django.utils.importlib import import_module

class Price(object):
    gross = None
    net = None

    def __unicode__(self):
        return u"net=%s,gross=%s" % (self.net, self.gross)

    def __repr__(self):
        return "net=%s,gross=%s" % (self.net, self.gross)

    def __init__(self, net=None, gross=None):
        self.net = Decimal(net) if net else None
        if gross is None:
            self.gross = self.net
        else:
            self.gross = Decimal(gross) if gross else None

    def __eq__(self, other):
        if isinstance(other, Price):
            return self.gross == other.gross and self.net == other.net
        return False

class StopPropagation(Exception):
    pass


processors_queue = []
for handler in settings.SATCHLESS_PRICING_HANDLERS:
    if isinstance(handler, str):
        mod_name, han_name = handler.rsplit('.', 1)
        module = import_module(mod_name)
        handler = getattr(module, han_name)
    processors_queue.append(handler)

def get_variant_price(variant, quantity=1, **kwargs):
    price = Price()
    for handler in processors_queue:
        try:
            price = handler.get_variant_price(variant, quantity=quantity, price=price, **kwargs)
        except StopPropagation:
            break
    return price

def get_product_price_range(product, **kwargs):
    price = Price()
    for handler in processors_queue:
        try:
            price = handler.get_product_price_range(product, price=price, **kwargs)
        except StopPropagation:
            break
    return price

def get_cartitem_unit_price(cartitem, **kwargs):
    price = Price()
    for handler in processors_queue:
        try:
            price = handler.get_cartitem_unit_price(cartitem, price=price, **kwargs)
        except StopPropagation:
            break
    return price
