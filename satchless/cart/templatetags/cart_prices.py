from django import template

from ...pricing import Price
from ...product.templatetags.product_prices import BasePriceNode, parse_price_tag

register = template.Library()

class CartItemUnitPriceNode(BasePriceNode):
    def get_currency_for_item(self, item):
        return item.cart.currency

    def get_price(self, cartitem, pricing_handler, currency, **kwargs):
        return pricing_handler.get_variant_price(cartitem.variant.get_subtype_instance(),
                                                 currency=currency,
                                                 quantity=cartitem.quantity,
                                                 cart=cartitem.cart,
                                                 cartitem=cartitem, **kwargs)


class CartItemPriceNode(CartItemUnitPriceNode):
    def get_price(self, cartitem, *args, **kwargs):
        unit_price = super(CartItemPriceNode, self).get_price(cartitem, *args, **kwargs)
        return unit_price*cartitem.quantity


class CartTotalPriceNode(BasePriceNode):
    def get_currency_for_item(self, cart):
        return cart.currency

    def get_price(self, cart, pricing_handler, currency, **kwargs):
        get_variant_price = lambda cart_item: pricing_handler.get_variant_price(
            quantity=cart_item.quantity, currency=currency,
            variant=cart_item.variant.get_subtype_instance(), **kwargs)
        return sum([get_variant_price(ci)*ci.quantity for ci in cart.get_all_items()],
                    Price(0, currency=currency))

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

@register.tag
def cart_total_price(parser, token):
    try:
        return CartTotalPriceNode(*parse_price_tag(parser, token))
    except (ImportError, NotImplementedError):
        pass
    return ''
