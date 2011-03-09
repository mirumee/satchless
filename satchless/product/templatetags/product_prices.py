from django.conf import settings
from django.utils.datastructures import SortedDict
from django import template

register = template.Library()

@register.filter
def variant_price(variant, currency=getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None)):
    if not currency:
        return ''
    try:
        from satchless.pricing.handler import get_variant_price
        price = get_variant_price(variant, currency)
        if price is not None and price.has_value():
            return price
    except ImportError:
        pass
    return ''

@register.filter
def product_price_range(product, currency=getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None)):
    if not currency:
        return ''
    try:
        from satchless.pricing.handler import get_product_price_range
        min_price, max_price = get_product_price_range(product, currency)
        if min_price is not None and min_price.has_value():
            return SortedDict((('min', min_price), ('max', max_price)))
    except ImportError:
        pass
    return ''

@register.filter
def variant_price_chain(variant, currency=getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None)):
    if not currency:
        return ''
    try:
        from satchless.pricing.handler import get_variant_price_chain
        price = get_variant_price_chain(variant, currency)
    except ImportError:
        pass
    return ''

@register.filter
def product_price_range_chain(product, currency=getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None)):
    if not currency:
        return ''
    try:
        from satchless.pricing.handler import get_product_price_range_chain
        return get_product_price_range_chain(product, currency)
    except ImportError:
        pass
    return ''

@register.filter
def get_final_price(price_chain):
    return price_chain.values()[-1]

@register.filter
def get_handler_price(price_chain, handler_name):
    return price_chain[handler_name]

@register.filter
def get_final_price_range(price_chain):
    min_price, max_price = price_chain.values()[-1]
    return SortedDict((('min', min_price), ('max', max_price)))

@register.filter
def get_handler_price_range(price_chain, handler_name):
    min_price, max_price = price_chain[handler_name]
    return SortedDict((('min', min_price), ('max', max_price)))
