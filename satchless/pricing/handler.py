from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from satchless.util.exceptions import FinalValue

from . import Price, PricingHandler

if not getattr(settings, 'SATCHLESS_PRICING_HANDLERS', None):
    raise ImproperlyConfigured('You need to configure '
                               'SATCHLESS_PRICING_HANDLERS')

_handlers = None

def get_variant_price(variant, currency, quantity=1, **context):
    price = Price()
    for handler in _handlers:
        try:
            price = handler.get_variant_price(variant=variant,
                                              currency=currency,
                                              quantity=quantity, price=price,
                                              **context)
        except FinalValue, e:
            return e.value
    return price

def get_product_price_range(product, currency, **context):
    p_range = None
    for handler in _handlers:
        try:
            p_range = handler.get_product_price_range(product=product,
                                                      currency=currency,
                                                      price_range=p_range,
                                                      **context)
        except FinalValue, e:
            return e.value
    return p_range

def init_queue():
    global _handlers
    _handlers = []
    for item in settings.SATCHLESS_PRICING_HANDLERS:
        if isinstance(item, str):
            mod_name, attr_name = item.rsplit('.', 1)
            module = import_module(mod_name)
            if not hasattr(module, attr_name):
                raise ImproperlyConfigured(
                    '%s in SATCHLESS_PRICING_HANDLERS does not exist.' % item)
            item = getattr(module, attr_name)
        if isinstance(item, type):
            item = item()
        if not isinstance(item, PricingHandler):
            raise ImproperlyConfigured(
                '%s in SATCHLESS_PRICING_HANDLERS is not a proper subclass of '
                'satchless.pricing.PricingHandler' % item)
        _handlers.append(item)
init_queue()
