from django import template

register = template.Library()

@register.filter
def variant_price(variant):
    try:
        from satchless.pricing.handler import get_variant_price
        price = get_variant_price(variant)
        if price.has_value():
            return price
    except ImportError:
        pass
    return ''

@register.filter
def product_price_range(product):
    try:
        from satchless.pricing.handler import get_product_price_range
        price = get_product_price_range(product)
        if price.has_value():
            return price
    except ImportError:
        pass
    return ''
