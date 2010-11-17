from django import template

register = template.Library()

@register.filter
def variant_price(variant):
    try:
        from satchless.pricing import get_handler
        return get_handler().get_variant_price(variant=variant.get_subtype_instance())
    except (ImportError, NotImplementedError)
        return ''

@register.filter
def product_price_range(product):
    try:
        from satchless.pricing import get_handler
        return get_handler()(product=product.get_subtype_instance())
    except PriceException:
        return ''
