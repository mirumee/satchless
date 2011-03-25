from django import template

from ...product.templatetags.product_prices import BasePriceNode, parse_price_tag
from ...pricing import Price

register = template.Library()

def get_cartitem_unit_price(cartitem, currency=None, **kwargs):
    from satchless.pricing import handler
    variant = cartitem.variant.get_subtype_instance()
    currency = currency if currency else cartitem.cart.currency
    return handler.get_variant_price(variant, currency, quantity=cartitem.quantity,
                             cart=cartitem.cart, cartitem=cartitem, **kwargs)

class CartItemPriceNode(BasePriceNode):
    def get_currency_for_item(self, item):
        return item.cart.currency

    def get_price(self, cartitem, currency, **kwargs):
        price = get_cartitem_unit_price(cartitem, currency=currency)
        if price.has_value():
            return price * cartitem.quantity

class CartItemUnitPriceNode(BasePriceNode):
    def get_currency_for_item(self, item):
        return item.cart.currency

    def get_price(self, cartitem, currency, **kwargs):
        price = get_cartitem_unit_price(cartitem, currency=currency)
        if price.has_value():
            return price

@register.tag
def cartitem_price(parser, token):
    try:
        return CartItemPriceNode(*parse_price_tag(parser, token))
    except (ImportError, NotImplementedError):
        pass
    return ''

@register.tag
def cartitem_unit_price(parser, token):
    try:
        return CartItemUnitPriceNode(*parse_price_tag(parser, token))
    except (ImportError, NotImplementedError):
        pass
    return ''

@register.filter
def cart_total(cart):
    total = Price(0)
    for i in cart.items.all():
        total += get_cartitem_unit_price(i) * i.quantity
    return total
