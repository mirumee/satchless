# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ....product.models import NonConfigurableProductAbstract


class VariantStockLevelMixin(models.Model):
    """Mixin for configurable Variant models"""
    
    stock_level = models.DecimalField(_("stock level"), max_digits=10, decimal_places=4)
    
    class Meta:
        abstract = True
        
class NonConfigurableVariantStockLevelMixin(models.Model):
    """Mixin for non-configurable Variant models.
    
    Use with NonConfigurableProductWithStockLevel.
    """
    
    stock_level = models.DecimalField(_("stock level"), max_digits=10, decimal_places=4, null=True)
    
    class Meta:
        abstract = True
        
class NonConfigurableProductWithStockLevel(NonConfigurableProductAbstract):
    """A subclass of NonConfigurableProductAbstract for non-configurable Products with stock level tracking.
    
    Use with NonConfigurableVariantStockLevelMixin.
    """
    
    stock_level = models.DecimalField(_("stock level"), max_digits=10, decimal_places=4)

    def save(self, *args, **kwargs):
        super(NonConfigurableProductWithStockLevel, self).save(*args, **kwargs)
        
        variant = self.variants.get()
        if self.stock_level != variant.stock_level:
            variant.stock_level = self.stock_level
            variant.save()
            
    class Meta:
        abstract = True
        
