from django import template
from satchless.product.exceptions import PriceException

register = template.Library()

@register.filter
def variant_price(variant):
    try:
        return variant.get_subtype_instance().get_unit_price()
    except PriceException:
        return ''

@register.filter
def product_price_range(product):
    try:
        return product.get_subtype_instance().get_unit_price_range()
    except PriceException:
        return ''
