from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchless.product.models import ProductAbstract, Variant

class Dummy(ProductAbstract):
    dummy_attribute = models.CharField(_("dummy attribute"), max_length=30)

    class Meta:
        app_label = 'product'
        verbose_name = _("dummy")
        verbose_name_plural = _("dummies")


class DummyVariant(Variant):
    product = models.ForeignKey(Dummy, related_name='variants')
    COLOR_CHOICES = (('red', _("red")), ('green', _("green")), ('blue', _("blue")))
    color = models.CharField(_("color"), max_length=10, choices=COLOR_CHOICES)
    size = models.PositiveIntegerField(_("size"))

    class Meta:
        unique_together = ('product', 'color', 'size')
        app_label = 'product'
        verbose_name = _("dummy variant")
        verbose_name_plural = _("dummy variants")
