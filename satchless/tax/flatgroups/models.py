from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.product.models import Product

class TaxGroup(models.Model):
    name = models.CharField(_("group name"), max_length=100)
    rate = models.DecimalField(_("rate"), max_digits=4, decimal_places=2,
            help_text=_("Percentile rate"))
    products = models.ManyToManyField(Product)
    default = models.BooleanField(_("Is default group?"), required=False,
            help_text=_("Products not listed in other tax groups will go to the default one."))

    def save(self, *args, **kwargs):
        if self.default:
            q = TaxGroup.objects.filter(default=True)
            if self.pk:
                q = q.exclude(pk=self.pk)
            q.update(default=False)
        super(TaxGroup, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
