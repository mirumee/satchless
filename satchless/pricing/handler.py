from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
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
    for handler_setting in settings.SATCHLESS_PRICING_HANDLERS:
        if isinstance(handler_setting, str):
            mod_name, han_name = handler_setting.rsplit('.', 1)
            module = import_module(mod_name)
            handler = getattr(module, han_name)
        else:
            handler = handler_setting
        for method in ('get_variant_price', 'get_product_price_range'):
            if not callable(getattr(handler, method, None)):
                raise ImproperlyConfigured(
                    '%s in SATCHLESS_PRICING_HANDLERS does not implement %s() method' % (
                            handler_setting, method))
        _handlers.append(handler)
init()
