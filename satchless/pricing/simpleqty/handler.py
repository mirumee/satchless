from django.db.models import Sum, Min, Max
from satchless.pricing import Price
from . import models

def get_variant_price(variant, quantity=1, **kwargs):
    try:
        base_price = models.ProductPrice.objects.get(product=variant.product)
    except models.ProductPrice.DoesNotExist:
        return
    if base_price.qty_mode == 'product' and kwargs.has_key('cart'):
        quantity += kwargs['cart'].items.filter(variant__in=variant.product.variants.all())\
                    .aggregate(Sum('quantity'))['quantity__sum']
    try:
        price = base_price.qty_overrides.filter(min_qty__lte=quantity)\
                    .order_by('-min_qty')[0].price
    except IndexError:
        price = base_price.price
    try:
        offset = variant.variantpriceoffset.price_offset
    except models.VariantPriceOffset.DoesNotExist:
        offset = 0
    price = price + offset
    return Price(net=price, gross=price)

def get_product_price_range(product, **kwargs):
    try:
        base_price = models.ProductPrice.objects.get(product=product)
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
    return (Price(net=min_price, gross=min_price), Price(net=max_price, gross=max_price))

def get_cartitem_unit_price(cartitem, **kwargs):
    product = cartitem.variant.get_subtype_instance().product
    try:
        base_price = models.ProductPrice.objects.get(product=product)
    except models.ProductPrice.DoesNotExist:
        return
    if base_price.qty_mode == 'product':
        quantity = cartitem.cart.items.filter(variant__in=product.variants.all())\
                    .aggregate(Sum('quantity'))['quantity__sum']
    else:
        quantity = cartitem.quantity
    try:
        price_val = base_price.qty_overrides.filter(min_qty__lte=quantity)\
                    .order_by('-min_qty')[0].price
    except IndexError:
        price_val = base_price.price
    try:
        offset = cartitem.variant.variantpriceoffset.price_offset
    except models.VariantPriceOffset.DoesNotExist:
        offset = 0
    price = price_val + offset
    return Price(net=price, gross=price)
