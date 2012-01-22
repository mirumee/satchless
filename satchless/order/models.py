import datetime
import decimal
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
import random

from ..pricing import Price
from ..util import countries
from . import signals
from .exceptions import EmptyCart

class OrderManager(models.Manager):

    def get_from_cart(self, cart, instance=None):
        '''
        Create an order from the user's cart, possibly discarding any previous
        orders created for this cart.
        '''
        from .handler import partitioner_queue
        if cart.is_empty():
            raise EmptyCart("Cannot create empty order.")
        previous_orders = self.filter(cart=cart)
        if not instance:
            order = self.model.objects.create(cart=cart, user=cart.owner,
                                              currency=cart.currency)
        else:
            order = instance
            order.groups.all().delete()
        groups = partitioner_queue.partition(cart)
        for group in groups:
            delivery_group = order.create_delivery_group(group)
            for item in group:
                ordered_item = order.create_ordered_item(delivery_group, item)
                ordered_item.save()

        previous_orders = (previous_orders.exclude(pk=order.pk)
                                          .filter(status='checkout'))
        previous_orders.delete()
        return order


class Order(models.Model):
    """
    Add this to your concrete model:
    cart = models.ForeignKey(Cart, related_name='orders')
    """
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
    payment_type_name = models.CharField(_('name'), max_length=128, blank=True,
                                         editable=False)
    payment_type_description = models.TextField(_('description'), blank=True)
    payment_price = models.DecimalField(_('unit price'), max_digits=12,
                                        decimal_places=4, default=0,
                                        editable=False)
    token = models.CharField(max_length=32, blank=True, default='')

    objects = OrderManager()

    class Meta:
        # Use described string to resolve ambiguity of the word 'order' in English.
        abstract = True
        verbose_name = _('order (business)')
        verbose_name_plural = _('orders (business)')
        ordering = ('-last_status_change',)

    def __unicode__(self):
        return _('Order #%d') % self.id

    def save(self, *args, **kwargs):
        if not self.token:
            for i in xrange(100):
                token = ''.join(random.sample(
                                '0123456789abcdefghijklmnopqrstuvwxyz', 32))
                if not self.__class__.objects.filter(token=token).count():
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

    def get_subtotal(self):
        return sum([g.get_subtotal() for g in self.groups.all()],
                   Price(0, currency=self.currency))

    def get_delivery_price(self):
        return sum([g.get_delivery_price() for g in self.groups.all()],
                   Price(0, currency=self.currency))

    def get_payment_price(self):
        return Price(self.payment_price, currency=self.currency)

    def get_total(self):
        payment_price = self.get_payment_price()
        return payment_price + sum([g.get_total() for g in self.groups.all()],
                                   Price(0, currency=self.currency))

    def create_delivery_group(self, group):
        return self.groups.create(order=self,
                                  require_shipping_address=group.is_shipping)

    def create_ordered_item(self, delivery_group, item):
        price = item.get_unit_price()
        variant = item.variant.get_subtype_instance()
        name = unicode(variant)
        ordered_item = delivery_group.items.create(delivery_group=delivery_group,
                                                   product_variant=item.variant,
                                                   product_name=name,
                                                   quantity=item.quantity,
                                                   unit_price_net=price.net,
                                                   unit_price_gross=price.gross)
        return ordered_item


class DeliveryGroup(models.Model):
    """
    add this to your concrete model:
    order = models.ForeignKey(Order, related_name='groups')
    """
    delivery_price = models.DecimalField(_('unit price'),
                                         max_digits=12, decimal_places=4,
                                         default=0, editable=False)
    delivery_type = models.CharField(max_length=256, blank=True)
    delivery_type_name = models.CharField(_('name'), max_length=128, blank=True,
                                          editable=False)
    delivery_type_description = models.TextField(_('description'), blank=True,
                                                 editable=False)
    require_shipping_address = models.BooleanField(default=False, editable=False)
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

    def get_subtotal(self):
        return sum([i.price() for i in self.items.all()],
                   Price(0, currency=self.order.currency))

    def get_delivery_price(self):
        return Price(self.delivery_price, currency=self.order.currency)

    def get_total(self):
        delivery_price = self.get_delivery_price()
        return delivery_price + sum([i.price() for i in self.items.all()],
                                    Price(0, currency=self.order.currency))


class OrderedItem(models.Model):
    """
    add this to your concrete model:
    delivery_group = models.ForeignKey(DeliveryGroup, related_name='items')
    """
    product_name = models.CharField(max_length=128)
    quantity = models.DecimalField(_('quantity'),
                                   max_digits=10, decimal_places=4)
    unit_price_net = models.DecimalField(_('unit price (net)'),
                                         max_digits=12, decimal_places=4)
    unit_price_gross = models.DecimalField(_('unit price (gross)'),
                                           max_digits=12, decimal_places=4)

    class Meta:
        abstract = True

    def unit_price(self):
        return Price(net=self.unit_price_net, gross=self.unit_price_gross,
                     currency=self.delivery_group.order.currency)

    def price(self):
        net = self.unit_price_net * self.quantity
        gross = self.unit_price_gross * self.quantity
        return Price(net=net.quantize(decimal.Decimal('0.01')),
                     gross=gross.quantize(decimal.Decimal('0.01')),
                     currency=self.delivery_group.order.currency)
