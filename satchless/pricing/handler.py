from django.conf import settings
from django.utils.importlib import import_module

from . import Price, StopPropagation

_handlers_queue = None

def get_variant_price(variant, currency, quantity=1, **context):
    price = Price()
    for handler in _handlers_queue:
        try:
            price = handler.get_variant_price(variant, currency=currency,
                                              quantity=quantity, price=price,
                                              **context)
        except StopPropagation:
            break
    return price

def get_product_price_range(product, currency, **context):
    p_range = (Price(), Price())
    for handler in _handlers_queue:
        try:
            p_range = handler.get_product_price_range(product,
                                                      currency=currency,
                                                      price_range=p_range,
                                                      **context)
        except StopPropagation:
            break
    return p_range

def get_cartitem_unit_price(cartitem, currency, **context):
    price = Price()
    for handler in _handlers_queue:
        try:
            price = handler.get_cartitem_unit_price(cartitem, currency=currency,
                                                    price=price, **context)
        except StopPropagation:
            break
    return price

def init_queue():
    global _handlers_queue
    _handlers_queue = []
    for handler in settings.SATCHLESS_PRICING_HANDLERS:
        if isinstance(handler, str):
            mod_name, han_name = handler.rsplit('.', 1)
            module = import_module(mod_name)
            handler = getattr(module, han_name)
        _handlers_queue.append(handler)

init_queue()
