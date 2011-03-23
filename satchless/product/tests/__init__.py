from django.db import models

from ..models import *

#models for tests

class DeadParrot(ProductAbstract):
    species = models.CharField(max_length=20)

class DeadParrotVariant(Variant):
    product = models.ForeignKey(DeadParrot, related_name='variants')
    color = models.CharField(max_length=10,
                choices=(('blue', 'blue'), ('white', 'white'), ('red', 'red'), ('green', 'green')))
    looks_alive = models.BooleanField()

    def __unicode__(self):
        "For debugging purposes"
        return u"%s %s %s" % (
                "alive" if self.looks_alive else "resting",
                self.get_color_display(), self.product.slug)

    class Meta:
        unique_together = ('product', 'color', 'looks_alive')

from .product import *
from .pricing import *
