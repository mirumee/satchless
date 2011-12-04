from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..order.models import DeliveryGroup
from ..util import countries
from ..util.models import Subtyped

class DeliveryVariant(Subtyped):
    '''
    Base class for all delivery variants. This is what gets assigned to an
    order shipping group at the checkout step.
    '''
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('unit price'),
                                max_digits=12, decimal_places=4)

    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True


class PhysicalShippingVariant(DeliveryVariant):
    shipping_first_name = models.CharField(_("first name"), max_length=256)
    shipping_last_name = models.CharField(_("last name"), max_length=256)
    shipping_company_name = models.CharField(_("company name"),
                                             max_length=256, blank=True)
    shipping_street_address_1 = models.CharField(_("street address 1"),
                                                 max_length=256)
    shipping_street_address_2 = models.CharField(_("street address 2"),
                                                 max_length=256, blank=True)
    shipping_city = models.CharField(_("city"), max_length=256)
    shipping_postal_code = models.CharField(_("postal code"), max_length=20)
    shipping_country = models.CharField(_("country"),
                                        choices=countries.COUNTRY_CHOICES,
                                        max_length=2, blank=True)
    shipping_country_area = models.CharField(_("country administrative area"),
                                             max_length=128, blank=True)
    shipping_phone = models.CharField(_("phone number"),
                                      max_length=30, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s for %s, %s" % (self.name, self.shipping_full_name,
                                  self.get_shipping_country_display())

    @property
    def shipping_full_name(self):
        return u'%s %s' % (self.shipping_first_name, self.shipping_last_name)
