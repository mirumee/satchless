from django.db import models
import satchless.contrib.pricing.simpleqty.models

from categories.app import product_app

class PriceQtyOverride(satchless.contrib.pricing.simpleqty.models.PriceQtyOverride):
    product = models.ForeignKey(product_app.Product, related_name='qty_overrides')

    class Meta:
        ordering = ('min_qty',)


