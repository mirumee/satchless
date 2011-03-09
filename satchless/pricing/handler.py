from django.conf import settings
from django.utils.importlib import import_module
from django.utils.datastructures import SortedDict

from . import Price, StopPropagation

_handlers_queue = None

def get_variant_price(variant, currency, quantity=1, **context):
    price = Price()
    for handler in _handlers_queue.values():
        try:
            price = handler.get_variant_price(variant, currency=currency,
                                              quantity=quantity, price=price,
                                              **context)
        except StopPropagation:
            break
    return price

def get_product_price_range(product, currency, **context):
    p_range = (Price(), Price())
    for handler in _handlers_queue.values():
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
    for handler in _handlers_queue.values():
        try:
            price = handler.get_cartitem_unit_price(cartitem, currency=currency,
                                                    price=price, **context)
        except StopPropagation:
            break
    return price

def get_variant_price_chain(variant, currency, quantity=1, **context):
    price = Price()
    price_chain = SortedDict()
    for handler_name, handler in _handlers_queue.items():
        try:
            price = handler.get_variant_price(variant, currency=currency,
                                              quantity=quantity, price=price,
                                              **context)
            price_chain[handler_name] = price
        except StopPropagation:
            break
    return price_chain

def get_product_price_range_chain(product, currency, **context):
    price_range = {'min': Price(), 'max': Price()}
    price_range_chain = SortedDict()
    for handler_name, handler in _handlers_queue.items():
        try:
            price_range = handler.get_product_price_range(product,
                                                      currency=currency,
                                                      price_range=price_range,
                                                      **context)
            price_range_chain[handler_name] = price_range
        except StopPropagation:
            break
    return price_range_chain

def get_cartitem_unit_price_chain(cartitem, currency, **context):
    price = Price()
    price_chain = SortedDict()
    for handler_name, handler in _handlers_queue.items():
        try:
            price = handler.get_cartitem_unit_price(cartitem, currency=currency,
                                                    price=price, **context)
            price_chain[handler_name] = price
        except StopPropagation:
            break
    return price_chain

def init_queue():
    global _handlers_queue
    _handlers_queue = SortedDict()
    for handler in settings.SATCHLESS_PRICING_HANDLERS:
        if isinstance(handler, str):
            mod_name, han_name = handler.rsplit('.', 1)
            module = import_module(mod_name)
            _handlers_queue[handler] = getattr(module, han_name)
        else:
            _handlers_queue[handler] = handler

init_queue()
