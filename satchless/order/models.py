from countries.models import Country
import datetime
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..cart.models import Cart
from ..payment.models import PaymentVariant
from ..product.models import Variant
from ..delivery.models import DeliveryVariant
from .handler import partition

class OrderManager(models.Manager):
    def create_for_cart(self, cart):
        '''
        Create an order from the user's cart, possibly discarding any previous
        orders created for this cart.
        '''
        safe_statuses = ['checkout', 'payment-pending', 'cancelled']
        previous_orders = self.filter(cart=cart)
        if previous_orders.exclude(status__in=safe_statuses).exists():
            raise SuspiciousOperation('A paid order exists for this cart.')
        previous_orders.delete()
        order = Order.objects.create(cart=cart, user=cart.user)
        groups = partition(cart)
        for group in groups:
            delivery_group = order.groups.create()
            for item in group:
                delivery_group.items.create(product_variant=item.variant,
                                            product_name=unicode(item.variant),
                                            quantity=item.quantity,
                                            price=item.get_unit_price())
        return order

class Order(models.Model):
    STATUS_CHOICES = (
        ('checkout', _('undergoing checkout')),
        ('payment-pending', _('waiting for payment')),
        ('payment-complete', _('paid')),
        ('delivery', _('shipped')),
        ('cancelled', _('cancelled')),
    )
    status = models.CharField(_('order status'), max_length=32,
                              choices=STATUS_CHOICES, default='checkout')
    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, related_name='orders')
    cart = models.ForeignKey(Cart, blank=True, null=True, related_name='+')
    payment_variant = models.ForeignKey(PaymentVariant, blank=True,
                                        null=True, related_name='orders')
    billing_full_name = models.CharField(_("full person name"),
                                         max_length=256, blank=True)
    billing_company_name = models.CharField(_("company name"),
                                            max_length=256, blank=True)
    billing_street_address_1 = models.CharField(_("street address 1"),
                                                max_length=256, blank=True)
    billing_street_address_2 = models.CharField(_("street address 2"),
                                                max_length=256, blank=True)
    billing_city = models.CharField(_("city"), max_length=256, blank=True)
    billing_postal_code = models.CharField(_("postal code"),
                                           max_length=20, blank=True)
    billing_country = models.ForeignKey(Country, blank=True, null=True,
                                        related_name='+')
    billing_tax_id = models.CharField(_("tax ID"), max_length=40, blank=True)
    billing_phone = models.CharField(_("phone number"),
                                     max_length=30, blank=True)

    def __unicode__(self):
        return _('Order #%d') % self.id

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')


class DeliveryGroup(models.Model):
    order = models.ForeignKey(Order, related_name='groups')
    shipping_variant = models.ForeignKey(DeliveryVariant,
                                         related_name='delivery_groups')


class OrderedItem(models.Model):
    shipping_group = models.ForeignKey(DeliveryGroup, related_name='items')
    product_variant = models.ForeignKey(Variant, blank=True, null=True,
                                        related_name='+')
    product_name = models.CharField(max_length=128)
    quantity = models.DecimalField(_('quantity'),
                                   max_digits=10, decimal_places=4)
    price = models.DecimalField(_('unit price'),
                                max_digits=12, decimal_places=4)
