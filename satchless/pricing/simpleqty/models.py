from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchless.product.models import Product, Variant

class ProductQtyPrice(models.Model):
    """
    Holds price of product unit, depending of total quantity being sold.
    """
    product = models.ForeignKey(Product)
    min_qty = models.DecimalField(_("minimal quantity"))
    price = models.DecimalField(_("unit_price"), max_digits=12, decimal_places=4)

    class Meta:
        ordering = ('min_qty',)


class VariantPriceOffset(models.Model):
    """
    Holds optional price offset for a variant. Does not depend on quantity.
    """
    variant = models.ForeignKey(Variant, unique=True)
    price_offset = models.DecimalField(_("unit price offset"), max_digits=12, decimal_places=4)
