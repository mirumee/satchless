# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.product.models import Variant, Product

class StockLevel(models.Model):
    base_product = models.ForeignKey(Product, related_name="stock_levels")
    variant = models.OneToOneField(Variant)
    quantity = models.DecimalField(_("quantity"), max_digits=10, decimal_places=4)

    def clean(self):
        self.quantity = self.variant.get_subtype_instance().product.sanitize_quantity(self.quantity)

    def __unicode__(self):
        return u"%s × %s" % (self.variant, self.quantity)

