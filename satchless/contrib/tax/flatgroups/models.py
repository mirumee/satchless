from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.product.models import Product

class TaxGroup(models.Model):
    name = models.CharField(_("group name"), max_length=100)
    rate = models.DecimalField(_("rate"), max_digits=4, decimal_places=2,
            help_text=_("Percentile rate of the tax."))
    rate_name = models.CharField(_("name of the rate"), max_length=30,
            help_text=_("Name of the rate which will be displayed to the user."))
    products = models.ManyToManyField(Product,
            help_text=_("WARNING: Adding product to a group will remove it from other groups."))
    default = models.BooleanField(_("Is default group?"), default=False,
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

def _enforce_single_taxgroup(sender, instance, **kwargs):
    if isinstance(instance, TaxGroup):
        for p in instance.products.all():
            p.taxgroup_set.clear()
            p.taxgroup_set.add(instance)
models.signals.m2m_changed.connect(_enforce_single_taxgroup)
