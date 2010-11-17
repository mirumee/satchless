from django import template

register = template.Library()

@register.filter
def variant_price(variant):
    try:
        from satchless.pricing import get_variant_price
        return get_variant_price(variant.get_subtype_instance())
    except ImportError:
        return ''

@register.filter
def product_price_range(product):
    try:
        from satchless.pricing import get_product_price_range
        return get_product_price_range(product.get_subtype_instance())
    except ImportError:
        return ''
