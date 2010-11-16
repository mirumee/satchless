from django import template
from satchless.product.exceptions import PriceException

register = template.Library()

@register.filter
def cartitem_unit_price(cartitem):
    try:
        return cartitem.get_unit_price()
    except PriceException:
        return ''

@register.filter
def cartitem_price(cartitem):
    try:
        return cartitem.get_unit_price() * cartitem.quantity
    except PriceException:
        return ''

@register.filter
def cart_total(cart):
    try:
        return cart.get_total_price()
    except PriceException:
        return ''
