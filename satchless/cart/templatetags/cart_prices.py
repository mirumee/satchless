from django import template

register = template.Library()

@register.filter
def cartitem_unit_price(cartitem):
    try:
        from satchless.pricing import get_handler
        return get_handler().get_cartitem_unit_price(cartitem)
    except (ImportError, NotImplementedError):
        return ''

@register.filter
def cartitem_price(cartitem):
    try:
        from satchless.pricing import get_handler
        return get_handler().get_cartitem_unit_price(cartitem)
    except (ImportError, NotImplementedError):
        return ''

@register.filter
def cart_total(cart):
    try:
        return cart.get_total_price()
    except (ImportError, NotImplementedError):
        return ''
