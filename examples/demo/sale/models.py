# -*- coding:utf-8 -*-
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.pricing import PriceRange

class DiscountGroup(models.Model):
    name = models.CharField(_('group name'), max_length=100)
    rate = models.DecimalField(_('rate'), max_digits=4, decimal_places=2,
                               help_text=_('Percentile rate of the discount.'))
    rate_name = models.CharField(_('name of the rate'), max_length=30,
                                 help_text=_(u'Name of the rate which will be '
                                             'displayed to the user.'))

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


class DiscountedProduct(models.Model):
    discount = models.ForeignKey(DiscountGroup, null=True, blank=True,
                                 related_name='products')

    class Meta:
        abstract = True
