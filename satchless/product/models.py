# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
import decimal

from ..util.models import Subtyped

__all__ = ('Product', 'Variant')

class Product(Subtyped):
    """
    The base Product to rule them all. Provides slug, a powerful item to
    identify member of each tribe.
    """
    slug = models.SlugField(_('slug'), max_length=80, db_index=True,
                            unique=True,
                            help_text=_('Slug will be used in the address of'
                                        ' the product page. It should be'
                                        ' URL-friendly (letters, numbers,'
                                        ' hyphens and underscores only) and'
                                        ' descriptive for the SEO needs.'))

    quantity_quantizer = decimal.Decimal(1)
    quantity_rounding = decimal.ROUND_HALF_UP

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.slug

    @models.permalink
    def get_absolute_url(self, category=None):
        categories = getattr(self, 'categories', None)
        if categories and categories.count() > 0:
            return categories.get_product_url(product=self, category=category)

        return 'product:details', (self.pk, self.slug)

    def quantize_quantity(self, quantity):
        """
        Returns sanitized quantity. By default it rounds the value to the
        nearest integer.
        """
        return decimal.Decimal(quantity).quantize(self.quantity_quantizer,
                                                  rounding=self.quantity_rounding)


class Variant(Subtyped):
    """
    Base class for variants. It identifies a concrete product instance,
    which goes to a cart. Custom variants inherit from it.
    """
    class Meta:
        abstract = True
