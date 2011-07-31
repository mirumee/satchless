# -*- coding:utf-8 -*-
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.product.models import Product
from satchless.pricing import PriceRange

class DiscountGroup(models.Model):
    name = models.CharField(_("group name"), max_length=100)
    rate = models.DecimalField(_("rate"), max_digits=4, decimal_places=2,
            help_text=_("Percentile rate of the discount."))
    rate_name = models.CharField(_("name of the rate"), max_length=30,
            help_text=_("Name of the rate which will be displayed to the user."))
    products = models.ManyToManyField(Product, related_name='discount', blank=True,
            help_text=_("WARNING: Adding product to a discount's group will remove it from other groups."))

    def get_discount_amount(self, price):
        multiplier = (Decimal('100') - self.rate) / Decimal('100')
        if isinstance(price, PriceRange):
            min_price = price.min_price * multiplier
            max_price = price.max_price * multiplier
            return PriceRange(min_price=min_price, max_price=max_price)
        else:
            return price * multiplier

    def __unicode__(self):
        return self.name

DiscountGroup.products.through._meta.verbose_name_plural = u"Discounted products"

def _enforce_single_discountgroup(sender, instance, **kwargs):
    if isinstance(instance, DiscountGroup):
        for p in instance.products.all():
            p.discount.clear()
            p.discount.add(instance)
models.signals.m2m_changed.connect(_enforce_single_discountgroup)
