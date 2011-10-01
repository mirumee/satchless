# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..util.models import Subtyped

__all__ = ('ProductAbstract', 'Variant')

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

    def __unicode__(self):
        return self.slug

    @models.permalink
    def get_absolute_url(self, category=None):
        categories = getattr(self, 'categories', None)
        if categories and categories.count() > 0:
            return categories.get_product_url(product=self, category=category)

        return 'satchless-product-details', (self.pk, self.slug)

    def sanitize_quantity(self, quantity):
        """
        Returns sanitized quantity. By default it rounds the value to the
        nearest integer.
        """
        return Decimal(quantity).quantize(1)


class ProductAbstract(Product):
    """
    Base class for every product to inherit from.
    """
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
                                        help_text=_('Description used by search'
                                                    ' and indexing engines.'))

    class Meta:
        abstract = True


class Variant(Subtyped):
    """
    Base class for variants. It identifies a concrete product instance,
    which goes to a cart. Custom variants inherit from it.
    """
    sku = models.CharField(_('SKU'), max_length=128, db_index=True, unique=True,
                           help_text=_('ID of the product variant used'
                                       ' internally in the shop.'))

    def __unicode__(self):
        return '%s' % self.sku
