from django.db.models import Sum, Min, Max
from satchless.product.signals import product_unit_price_range_query, variant_unit_price_query
from satchless.cart.signals import cartitem_unit_price_query
from . import models

def product_unit_price_range_listener(sender, instance=None, price_range=None, **kwargs):
    try:
        base_price = models.ProductPrice.objects.get(product=instance)
    except models.ProductPrice.DoesNotExist:
        return
    try:
        price = base_price.qty_overrides.filter(min_qty__lte=1).order_by('-min_qty')[0].price
    except IndexError:
        price = base_price.price
    min_offset = base_price.offsets.aggregate(Min('price_offset'))['price_offset__min']
    max_offset = base_price.offsets.aggregate(Max('price_offset'))['price_offset__max']
    max_price = max(price, price + max_offset)
    min_price = min(price, price + min_offset)
    price_range.append((min_price, max_price))


def variant_unit_price_listener(sender, instance=None, quantity=1, price=None, **kwargs):
    try:
        base_price = models.ProductPrice.objects.get(product=instance.product)
    except models.ProductPrice.DoesNotExist:
        return
    if base_price.qty_mode == 'product' and kwargs.has_key('cart'):
        quantity += kwargs['cart'].items.filter(variant__in=instance.product.variants.all())\
                    .aggregate(Sum('quantity'))['quantity__sum']
    try:
        price_val = base_price.qty_overrides.filter(min_qty__lte=quantity).order_by('-min_qty')[0].price
    except IndexError:
        price_val = base_price.price
    try:
        offset = instance.variantpriceoffset.price_offset
    except models.VariantPriceOffset.DoesNotExist:
        offset = 0
    price.append(price_val + offset)

def cartitem_unit_price_listener(sender, instance=None, price=None, **kwargs):
    product = instance.variant.get_subtype_instance().product
    try:
        base_price = models.ProductPrice.objects.get(product=product)
    except models.ProductPrice.DoesNotExist:
        return
    if base_price.qty_mode == 'product':
        quantity = instance.cart.items.filter(variant__in=product.variants.all())\
                    .aggregate(Sum('quantity'))['quantity__sum']
    else:
        quantity = instance.quantity
    try:
        price_val = base_price.qty_overrides.filter(min_qty__lte=instance.quantity)\
                    .order_by('-min_qty')[0].price
    except IndexError:
        price_val = base_price.price
    try:
        offset = instance.variant.variantpriceoffset.price_offset
    except models.VariantPriceOffset.DoesNotExist:
        offset = 0
    price.append(price_val + offset)


product_unit_price_range_query.connect(product_unit_price_range_listener)
variant_unit_price_query.connect(variant_unit_price_listener)
cartitem_unit_price_query.connect(cartitem_unit_price_listener)
