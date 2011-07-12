import datetime
import decimal
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
import random

from ..cart.models import Cart
from ..pricing import Price
from ..product.models import Variant
from ..util import countries
from . import signals

class EmptyCart(Exception):
    pass

class OrderManager(models.Manager):
    def get_from_cart(self, cart, instance=None):
        '''
        Create an order from the user's cart, possibly discarding any previous
        orders created for this cart. If session is given, the order ID will be
        stored there.
        '''
        from .handler import partition
        if cart.is_empty():
            raise EmptyCart("Cannot create empty order.")
        previous_orders = self.filter(cart=cart)
        if not instance:
            order = Order.objects.create(cart=cart, user=cart.owner,
                                         currency=cart.currency)
        else:
            order = instance
            order.groups.all().delete()
            try:
                order.paymentvariant.delete()
            except ObjectDoesNotExist:
                pass
        groups = partition(cart)
        for group in groups:
            delivery_group = order.groups.create(order=order)
            for item in group:
                price = item.get_unit_price()
                variant = item.variant.get_subtype_instance()
                name = unicode(variant)
                delivery_group.items.create(product_variant=item.variant,
                                            product_name=name,
                                            quantity=item.quantity,
                                            unit_price_net=price.net,
                                            unit_price_gross=price.gross)
        previous_orders = (previous_orders.exclude(pk=order.pk)
                                          .filter(status='checkout'))
        previous_orders.delete()
        return order

class Order(models.Model):
    STATUS_CHOICES = (
        ('checkout', _('undergoing checkout')),
        ('payment-pending', _('waiting for payment')),
        ('payment-complete', _('paid')),
        ('payment-failed', _('payment failed')),
        ('delivery', _('shipped')),
        ('cancelled', _('cancelled')),
    )
    # Do not set the status manually, use .set_status() instead.
    status = models.CharField(_('order status'), max_length=32,
                              choices=STATUS_CHOICES, default='checkout')
    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False, blank=True)
    last_status_change = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, related_name='orders')
    cart = models.ForeignKey(Cart, blank=True, null=True, related_name='orders')
    currency = models.CharField(max_length=3)
    billing_first_name = models.CharField(_("first name"),
                                          max_length=256, blank=True)
    billing_last_name = models.CharField(_("last name"),
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
    billing_country = models.CharField(_("country"),
                                       choices=countries.COUNTRY_CHOICES,
                                       max_length=2, blank=True)
    billing_country_area = models.CharField(_("country administrative area"),
                                            max_length=128, blank=True)
    billing_tax_id = models.CharField(_("tax ID"), max_length=40, blank=True)
    billing_phone = models.CharField(_("phone number"),
                                     max_length=30, blank=True)
    payment_type = models.CharField(max_length=256, blank=True)
    token = models.CharField(max_length=32, blank=True, default='')
    objects = OrderManager()

    def __unicode__(self):
        return _('Order #%d') % self.id

    def save(self, *args, **kwargs):
        if not self.token:
            for i in xrange(100):
                token = ''.join(random.sample(
                                '0123456789abcdefghijklmnopqrstuvwxyz', 32))
                if not Order.objects.filter(token=token).count():
                    self.token = token
                    break
        return super(Order, self).save(*args, **kwargs)

    @property
    def billing_full_name(self):
        return u'%s %s' % (self.billing_first_name, self.billing_last_name)

    def set_status(self, new_status):
        old_status = self.status
        self.status = new_status
        self.last_status_change = datetime.datetime.now()
        self.save()
        signals.order_status_changed.send(sender=type(self), instance=self,
                                          old_status=old_status)

    def subtotal(self):
        return sum([g.subtotal() for g in self.groups.all()],
                   Price(0, currency=self.currency))

    def delivery_price(self):
        return sum([g.delivery_price() for g in self.groups.all()],
                   Price(0, currency=self.currency))

    def payment_price(self):
        try:
            return Price(self.paymentvariant.price,
                         currency=self.currency)
        except ObjectDoesNotExist:
            return Price(0, currency=self.currency)

    def total(self):
        payment_price = self.payment_price()
        return payment_price + sum([g.total() for g in self.groups.all()],
                                   Price(0, currency=self.currency))

    class Meta:
        # Use described string to resolve ambiguity of the word 'order' in English.
        verbose_name = _('order (business)')
        verbose_name_plural = _('orders (business)')
        ordering = ('-last_status_change',)


class DeliveryGroup(models.Model):
    order = models.ForeignKey(Order, related_name='groups')
    delivery_type = models.CharField(max_length=256, blank=True)

    def subtotal(self):
        return sum([i.price() for i in self.items.all()],
                   Price(0, currency=self.order.currency))

    def delivery_price(self):
        try:
            return Price(self.deliveryvariant.price,
                         currency=self.order.currency)
        except ObjectDoesNotExist:
            return Price(0, currency=self.order.currency)

    def total(self):
        delivery_price = self.delivery_price()
        return delivery_price + sum([i.price() for i in self.items.all()],
                                    Price(0, currency=self.order.currency))


class OrderedItem(models.Model):
    delivery_group = models.ForeignKey(DeliveryGroup, related_name='items')
    product_variant = models.ForeignKey(Variant, blank=True, null=True,
                                        related_name='+',
                                        on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=128)
    quantity = models.DecimalField(_('quantity'),
                                   max_digits=10, decimal_places=4)
    unit_price_net = models.DecimalField(_('unit price (net)'),
                                         max_digits=12, decimal_places=4)
    unit_price_gross = models.DecimalField(_('unit price (gross)'),
                                           max_digits=12, decimal_places=4)

    def unit_price(self):
        return Price(net=self.unit_price_net, gross=self.unit_price_gross,
                     currency=self.delivery_group.order.currency)

    def price(self):
        net = self.unit_price_net * self.quantity
        gross = self.unit_price_gross * self.quantity
        return Price(net=net.quantize(decimal.Decimal('0.01')),
                     gross=gross.quantize(decimal.Decimal('0.01')),
                     currency=self.delivery_group.order.currency)
