from django.db import models
from django.utils.translation import ugettext_lazy as _
import decimal

from ..item import ItemRange, Item
from ..util.models import Subtyped

__all__ = ('Product', 'Variant')


class Product(Subtyped, ItemRange):
    """
    Django binding for a product group (product with multiple variants)
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

    def __repr__(self):
        return '<Product #%r: %r>' % (self.id, self.slug)

    def __iter__(self):
        return iter(self.variants.all())

    @models.permalink
    def get_absolute_url(self):
        return 'product:details', (self.pk, self.slug)

    def quantize_quantity(self, quantity):
        """
        Returns sanitized quantity. By default it rounds the value to the
        nearest integer.
        """
        return decimal.Decimal(quantity).quantize(
            self.quantity_quantizer, rounding=self.quantity_rounding)


class Variant(Subtyped, Item):
    """
    Django binding for a single product or variant
    """
    class Meta:
        abstract = True

    def __repr__(self):
        return '<Variant #%r>' % (self.id,)
