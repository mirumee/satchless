from django import template

register = template.Library()

@register.filter
def cartitem_unit_price(cartitem):
    try:
        from satchless.pricing.handler import get_cartitem_unit_price
        return get_cartitem_unit_price(cartitem)
    except ImportError:
        return ''

@register.filter
def cartitem_price(cartitem):
    try:
        from satchless.pricing.handler import get_cartitem_unit_price
        return get_cartitem_unit_price(cartitem)
    except (ImportError, NotImplementedError):
        return ''

@register.filter
def cart_total(cart):
    return cart.get_total_price()
