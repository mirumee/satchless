from product.signals import product_unit_price_range_query, variant_unit_price_query
from . import models

def product_unit_price_range_listener(sender, instance=None, **kwargs):
    base_price = models.ProductQtyPrice.objects\
                    .filter(product=instance, quantity__lte=1)\
                    .order_by('-quantity')[0].price
    offsets = models.VariantPriceOffset.objects\
                    .filter(variant__product=instance)
    min_ofset = offsets.order_by('price_offset')[0].price_ofset
    max_ofset = offsets.order_by('-price_offset')[0].price_offset
    # TODO: find variants with no offsets
    max_price = max(base_price, base_price + max_offset)
    min_price = min(base_price, base_price + min_offset)
    instance.unit_price_range = (min_price, max_price)
