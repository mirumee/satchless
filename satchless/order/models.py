import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_prices.models import PriceField
from prices import Price
import random

from ..item import ItemSet, ItemLine
from ..util import countries
from ..util.models import DeferredForeignKey
from . import signals


class PaymentInfo(ItemLine):
    name = None
    price = None
    description = None

    def __init__(self, name, price, description):
        self.name = name
        self.price = price
        self.description = description

    def get_price_per_item(self, **kwargs):
        return self.price


class Order(models.Model, ItemSet):

    STATUS_CHOICES = (
        ('checkout', _('undergoing checkout')),
        ('payment-pending', _('waiting for payment')),
        ('payment-complete', _('paid')),
        ('payment-failed', _('payment failed')),
        ('delivery', _('shipped')),
        ('cancelled', _('cancelled')),
    )
    cart = DeferredForeignKey('cart', blank=True, null=True,
                              related_name='orders')
    # Do not set the status manually, use .set_status() instead.
    status = models.CharField(_('order status'), max_length=32,
                              choices=STATUS_CHOICES, default='checkout')
    created = models.DateTimeField(default=datetime.datetime.now,
                                   editable=False, blank=True)
    last_status_change = models.DateTimeField(default=datetime.datetime.now,
                                              editable=False, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, related_name='+')
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
    payment_price = PriceField(_('unit price'),
                               currency=settings.SATCHLESS_DEFAULT_CURRENCY,
                               max_digits=12, decimal_places=4, default=0,
                               editable=False)
    token = models.CharField(max_length=32, blank=True, default='')

    class Meta:
        # Use described string to resolve ambiguity of the word 'order' in English.
        abstract = True
        verbose_name = _('order (business)')
        verbose_name_plural = _('orders (business)')
        ordering = ('-last_status_change',)

    def __iter__(self):
        for g in self.get_groups():
            yield g
        payment = self.get_payment()
        if payment:
            yield payment

    def __repr__(self):
        return '<Order #%r>' % (self.id,)

    def get_default_currency(self):
        return settings.SATCHLESS_DEFAULT_CURRENCY

    def save(self, *args, **kwargs):
        if not self.token:
            for i in xrange(100):
                token = ''.join(
                    random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 32))
                if not type(self).objects.filter(token=token).exists():
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

    def get_groups(self):
        return self.groups.all()

    def get_delivery_price(self):
        return sum([g.get_delivery().get_total() for g in self.get_groups()],
                   Price(0, currency=settings.SATCHLESS_DEFAULT_CURRENCY))

    def get_payment(self):
        return PaymentInfo(name=self.payment_type_name,
                           price=self.payment_price,
                           description=self.payment_type_description)

    def create_delivery_group(self, group):
        return self.groups.create(order=self,
                                  require_shipping_address=group.is_shipping)

    def is_empty(self):
        return not self.groups.exists()


class DeliveryInfo(ItemLine):
    name = None
    price = None
    description = None

    def __init__(self, name, price, description):
        self.name = name
        self.price = price
        self.description = description

    def get_price_per_item(self, **kwargs):
        return self.price


class DeliveryGroup(models.Model, ItemSet):

    order = DeferredForeignKey('order', related_name='groups', editable=False)
    delivery_price = PriceField(_('unit price'),
                                currency=settings.SATCHLESS_DEFAULT_CURRENCY,
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

    def __iter__(self):
        for i in self.get_items():
            yield i
        delivery = self.get_delivery()
        if delivery:
            yield delivery

    def get_default_currency(self):
        return settings.SATCHLESS_DEFAULT_CURRENCY

    def get_delivery(self):
        return DeliveryInfo(name=self.delivery_type_name,
                            price=self.delivery_price,
                            description=self.delivery_type_description)

    def get_items(self):
        return self.items.all()

    def add_item(self, variant, quantity, price, product_name=None):
        product_name = product_name or unicode(variant)
        return self.items.create(product_variant=variant, quantity=quantity,
                                 unit_price_net=price.net, product_name=product_name,
                                 unit_price_gross=price.gross)


class OrderedItem(models.Model, ItemLine):

    delivery_group = DeferredForeignKey('delivery_group', related_name='items',
                                        editable=False)
    product_variant = DeferredForeignKey('variant', blank=True, null=True,
                                         related_name='+',
                                         on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=128)
    quantity = models.DecimalField(_('quantity'),
                                   max_digits=10, decimal_places=4)
    unit_price_net = models.DecimalField(_('unit price (net)'),
                                         max_digits=12, decimal_places=4)
    unit_price_gross = models.DecimalField(_('unit price (gross)'),
                                           max_digits=12, decimal_places=4)

    class Meta:
        abstract = True

    def get_price_per_item(self, **kwargs):
        return Price(net=self.unit_price_net, gross=self.unit_price_gross,
                     currency=settings.SATCHLESS_DEFAULT_CURRENCY)

    def get_quantity(self):
        return self.quantity
