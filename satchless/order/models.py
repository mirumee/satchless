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
