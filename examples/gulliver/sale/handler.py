from django.db.models import Sum, Min, Max

from satchless.pricing import Price
from . import models

def _discount_product(product, price):
    try:
        group = product.discount.get()
    except models.DiscountGroup.DoesNotExist:
        return price
    if isinstance(price, Price):
        return group.get_discount_amount(price)
    elif isinstance(price, tuple):
        return (group.get_discount_amount(price[0]), group.get_discount_amount(price[1]))
    raise TypeError("Price must be a Price instance or tuple.")

def get_variant_price(variant, currency, **context):
    if context.get('discount', True):
        return _discount_product(variant.product, context.pop('price'))
    return context.pop('price')

def get_product_price_range(product, currency, **context):
    if context.get('discount', True):
        return _discount_product(product, context.pop('price_range'))
    return context.pop('price_range')

def get_cartitem_unit_price(cartitem, **context):
    if context.get('discount', True):
        return _discount_product(cartitem.variant.get_subtype_instance().product,
                                 context.pop('price'))
    return context.pop('price')
