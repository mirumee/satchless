from countries.models import Country
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..payment.models import PaymentVariant
from ..product.models import Variant
from ..shipping.models import ShippingVariant

class Order(models.Model):
    created = models.DateTimeField(default=datetime.datatime.now,
                                   editable=False, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    payment_variant = models.ForeignKey(PaymentVariant)
    billing_full_name = models.CharField(_("full person name"), max_length=256)
    billing_company_name = models.CharField(_("company name"), max_length=256, blank=True)
    billing_street_address_1 = models.CharField(_("street address 1"), max_length=256)
    billing_street_address_2 = models.CharField(_("street address 2"), max_length=256, blank=True)
    billing_city = models.CharField(_("city"), max_length=256)
    billing_postal_code = models.CharField(_("postal code"), max_length=20)
    billing_country = models.ForeignKey(Country)
    billing_tax_id = models.CharField(_("tax ID"), max_length=40, blank=True)
    billing_phone = models.CharField(_("phone number"), max_length=30, blank=True)

    def __unicode__(self):
        return _('Order #%d') % self.id

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')


class ShippingGroup(models.Model):
    order = models.ForeignKey(Order, related_name='groups')
    shipping_variant = models.ForeignKey(ShippingVariant)


class OrderedItem(models.Model):
    shipping_group = models.ForeignKey(ShippingGroup, related_name='items')
    product_variant = models.ForeignKey(Variant, blank=True, null=True)
    product_name = models.CharField(max_length=128)
    quantity = models.DecimalField(_('quantity'),
                                   max_digits=10, decimal_places=4)
    price = models.DecimalField(_('unit price'),
                                max_digits=12, decimal_places=4)
