from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchless.product.models import Variant
from satchless.image.models import Image

class ProductSet(models.Model):
    name = models.CharField(_('name'), max_length=128)
    slug = models.SlugField(max_length=50)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
            help_text=_("Description used by search and indexing engines"))

    @models.permalink
    def get_absolute_url(self):
        return ('satchless-productset-details', (self.slug,))

    class Meta:
        verbose_name = _("product set")
        verbose_name_plural = _("product sets")

    def variant_instances(self):
        return [psi.variant.get_subtype_instance() for psi in self.items.all()]

class ProductSetItem(models.Model):
    productset = models.ForeignKey(ProductSet, related_name='items')
    variant = models.ForeignKey(Variant)
    sort = models.PositiveIntegerField()

    def __unicode__(self):
        return u"Default variant %s" % self.variant

    class Meta:
        ordering = ['sort', 'id']
        verbose_name = _("set item")
        verbose_name_plural = _("set items")

class ProductSetImage(Image):
    product = models.ForeignKey(ProductSet, related_name='images')
    sort = models.PositiveIntegerField()

    class Meta:
        ordering = ['sort', 'id']
