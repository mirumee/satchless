from django import template

register = template.Library()

@register.filter
def cartitem_unit_price(cartitem, currency=None):
    try:
        from satchless.pricing.handler import get_cartitem_unit_price
        price = get_cartitem_unit_price(cartitem, currency if currency else cartitem.cart.currency)
        if price.has_value():
            return price
    except ImportError:
        pass
    return ''

@register.filter
def cartitem_price(cartitem, currency=None):
    try:
        from satchless.pricing.handler import get_cartitem_unit_price
        price = get_cartitem_unit_price(cartitem, currency if currency else cartitem.cart.currency)
        if price.has_value():
            return price * cartitem.quantity
    except (ImportError, NotImplementedError):
        pass
    return ''

@register.filter
def cart_total(cart):
    return cart.get_total_price()
