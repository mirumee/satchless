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
    price = context.pop('price')
    variant.price_without_discount = price
    return _discount_product(variant.product, price)

def get_product_price_range(product, currency, **context):
    price_range = context.pop('price_range')
    product.price_range_without_discount = price_range
    return _discount_product(product, price_range)

def get_cartitem_unit_price(cartitem, **context):
    price = context.pop('price')
    cartitem.price_without_discount = price
    return _discount_product(cartitem.variant.get_subtype_instance().product, price)
