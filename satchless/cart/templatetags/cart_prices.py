from django import template

from ...product.templatetags.product_prices import BasePriceNode, parse_price_tag

register = template.Library()


class CartItemUnitPriceNode(BasePriceNode):
    def get_price(self, cartitem, **kwargs):
        return cartitem.get_price_per_item(**kwargs)


class CartItemPriceNode(BasePriceNode):
    def get_price(self, cartitem, **kwargs):
        return cartitem.get_total(**kwargs)


class CartTotalPriceNode(BasePriceNode):
    def get_currency_for_item(self, cart):
        return cart.currency

    def get_price(self, cart, **kwargs):
        return cart.get_total(**kwargs)


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
