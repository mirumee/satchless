# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class VariantStockLevelMixin(models.Model):
    """
    Mixin for configurable Variant models
    """
    sku = models.CharField(_('SKU'), max_length=128, db_index=True, unique=True,
                           help_text=_('ID of the product variant used'
                                       ' internally in the shop.'))
    stock_level = models.DecimalField(_("stock level"), max_digits=10,
                                      decimal_places=4, default=0)

    class Meta:
        abstract = True
