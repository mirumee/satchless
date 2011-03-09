from django.conf import settings
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
            return {'min': min_price, 'max': max_price}
    except ImportError:
        pass
    return ''
