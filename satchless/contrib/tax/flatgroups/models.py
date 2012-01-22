from django.db import models
from django.utils.translation import ugettext_lazy as _

class TaxGroup(models.Model):

    name = models.CharField(_("group name"), max_length=100)
    rate = models.DecimalField(_("rate"), max_digits=4, decimal_places=2,
                               help_text=_("Percentile rate of the tax."))
    rate_name = models.CharField(_("name of the rate"), max_length=30,
                                 help_text=_("Name of the rate which will be"
                                             " displayed to the user."))
    def __unicode__(self):
        return self.name


class TaxedProductMixin(models.Model):

    tax_group = models.ForeignKey(TaxGroup, related_name='products',
                                  null=True)
    class Meta:
        abstract = True
