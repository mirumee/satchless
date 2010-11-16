from satchless.product.signals import product_unit_price_range_query, variant_unit_price_query
from . import models

def product_unit_price_range_listener(sender, instance=None, price_range=None, **kwargs):
    base_price = models.ProductQtyPrice.objects\
                    .filter(product=instance, min_qty__lte=1)\
                    .order_by('-min_qty')[0].price
    offsets = models.VariantPriceOffset.objects\
                    .filter(variant__in=instance.get_subtype_instance().variants.all())
    min_offset = offsets.order_by('price_offset')[0].price_offset
    max_offset = offsets.order_by('-price_offset')[0].price_offset
    max_price = max(base_price, base_price + max_offset)
    min_price = min(base_price, base_price + min_offset)
    price_range.append((min_price, max_price))


def variant_unit_price_listener(sender, instance=None, quantity=1, price=None, **kwargs):
    base_price = models.ProductQtyPrice.objects\
                    .filter(product=instance.product, min_qty__lte=quantity)\
                    .order_by('-min_qty')[0].price
    try:
        offset = instance.variantpriceoffset_set.get().price_offset
    except models.VariantPriceOffset.DoesNotExist:
        offset = 0
    price.append(base_price + offset)


product_unit_price_range_query.connect(product_unit_price_range_listener)
variant_unit_price_query.connect(variant_unit_price_listener)
