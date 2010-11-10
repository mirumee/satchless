from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.product.models import ProductAbstract, Variant, ProductAbstractTranslation

class Parrot(ProductAbstract):
    latin_name = models.CharField(max_length=20)

    class Meta:
        app_label = 'product'


class ParrotTranslation(ProductAbstractTranslation):
    pass


class ParrotVariant(Variant):
    product = models.ForeignKey(Parrot, related_name='variants')
    COLOR_CHOICES = (('red', _("red")), ('green', _("green")), ('blue', _("blue")))
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    looks_alive = models.BooleanField()

    def __unicode__(self):
        return u"%s %s %s" % (
                _("Alive") if self.looks_alive else _("Dead"),
                self.get_color_display(),
                self.product.name)

    class Meta:
        app_label = 'product'
        unique_together = ('product', 'color', 'looks_alive')
