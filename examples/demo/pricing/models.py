from django.db import models
import satchless.contrib.pricing.simpleqty.models

from categories.app import product_app

class ProductPrice(satchless.contrib.pricing.simpleqty.models.ProductPrice):
    product = models.OneToOneField(product_app.Product)


class PriceQtyOverride(satchless.contrib.pricing.simpleqty.models.PriceQtyOverride):
    """
    Overrides price of product unit, depending of total quantity being sold.
    """
    base_price = models.ForeignKey(ProductPrice, related_name='qty_overrides')

    class Meta:
        ordering = ('min_qty',)


class VariantPriceOffset(satchless.contrib.pricing.simpleqty.models.VariantPriceOffset):
    base_price = models.ForeignKey(ProductPrice, related_name='offsets')
    variant = models.OneToOneField(product_app.Variant, related_name='price_offset')
