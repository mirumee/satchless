from django.conf import settings
from django.utils.importlib import import_module

from satchless.util.exceptions import FinalValue

from . import Price

_handlers = None

def get_variant_price(variant, currency, quantity=1, **context):
    price = Price()
    for handler in _handlers:
        try:
            price = handler.get_variant_price(variant=variant, currency=currency,
                                              quantity=quantity, price=price,
                                              **context)
        except FinalValue, e:
            return e.value
    return price

def get_product_price_range(product, currency, **context):
    p_range = (Price(), Price())
    for handler in _handlers:
        try:
            p_range = handler.get_product_price_range(product=product, currency=currency,
                                                      price_range=p_range,
                                                      **context)
        except FinalValue, e:
            return e.value
    return p_range

def init():
    global _handlers
    _handlers = []
    for handler in settings.SATCHLESS_PRICING_HANDLERS:
        if isinstance(handler, str):
            mod_name, han_name = handler.rsplit('.', 1)
            module = import_module(mod_name)
            _handlers.append(getattr(module, han_name))
        else:
            _handlers.append(handler)

init()
