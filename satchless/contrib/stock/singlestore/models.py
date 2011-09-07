# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class VariantStockLevelMixin(models.Model):
    """
    Mixin for configurable Variant models
    """
    stock_level = models.DecimalField(_("stock level"), max_digits=10,
                                      decimal_places=4)

    class Meta:
        abstract = True
