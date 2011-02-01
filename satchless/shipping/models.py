from countries.models import Country
from django.conf import settings
from django.db import models
from mothertongue.models import MothertongueModelTranslate

from ..util.models import Subtyped

class ShippingVariant(MothertongueModelTranslate, Subtyped):
    '''
    Base class for all shipping variants. This is what gets assigned to an
    order shipping group at the checkout step.
    '''
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('unit price'),
                                max_digits=12, decimal_places=4)

    def __unicode__(self):
        return self.name


class ShippingVariantTranslation(models.Model):
    language = models.CharField(max_length=5, choices=settings.LANGUAGES[1:])
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)

    def __unicode__(self):
        return "%s@%s" % (self.name, self.language)


class PhysicalShippingVariant(ShippingVariant):
    shipping_full_name = models.CharField(_("full person name"), max_length=256)
    shipping_company_name = models.CharField(_("company name"),
                                             max_length=256, blank=True)
    shipping_street_address_1 = models.CharField(_("street address 1"),
                                                 max_length=256)
    shipping_street_address_2 = models.CharField(_("street address 2"),
                                                 max_length=256, blank=True)
    shipping_city = models.CharField(_("city"), max_length=256)
    shipping_postal_code = models.CharField(_("postal code"), max_length=20)
    shipping_country = models.ForeignKey(Country)
    shipping_phone = models.CharField(_("phone number"),
                                      max_length=30, blank=True)

    class Meta:
        abstract = True
