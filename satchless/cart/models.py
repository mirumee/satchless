# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
import random

from ..util.models import DeferredForeignKey
from . import signals

def get_default_currency():
    return settings.SATCHLESS_DEFAULT_CURRENCY

class QuantityResult(object):

    def __init__(self, cart_item, new_quantity, quantity_delta, reason=None):
        self.cart_item = cart_item
        self.new_quantity = new_quantity
        self.quantity_delta =  quantity_delta
        self.reason = reason


class Cart(models.Model):

    owner = models.ForeignKey(User, null=True, blank=True, related_name='+')
    typ = models.CharField(_("type"), max_length=100)
    currency = models.CharField(_("currency"), max_length=3,
                                default=get_default_currency)
    token = models.CharField(max_length=32, blank=True, default='')

    class Meta:
        abstract = True

    def __unicode__(self):
        if self.owner:
            return u"%s of %s" % (self.typ, self.owner.username)
        else:
            return self.typ

    def save(self, *args, **kwargs):
        if not self.token:
            for i in xrange(100):
                token = ''.join(
                    random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 32))
                if not type(self).objects.filter(token=token).exists():
                    self.token = token
                    break
        return super(Cart, self).save(*args, **kwargs)

    def add_item(self, variant, quantity, dry_run=False, **kwargs):
        variant = variant.get_subtype_instance()
        quantity = variant.product.quantize_quantity(quantity)
        try:
            item = self.get_item(variant=variant, **kwargs)
            old_qty = item.quantity
        except ObjectDoesNotExist:
            item = None
            old_qty = Decimal(0)
        quantity += old_qty
        result = []
        reason = u""
        signals.cart_quantity_change_check.send(sender=type(self),
                                                instance=self,
                                                variant=variant,
                                                old_quantity=old_qty,
                                                new_quantity=quantity,
                                                result=result)
        assert len(result) <= 1
        if len(result) == 1:
            quantity, reason = result[0]
        if not dry_run:
            if not quantity:
                if item:
                    item.delete()
            else:
                if item:
                    item.quantity = quantity
                    item.save()
                else:
                    item = self.items.create(variant=variant, quantity=quantity,
                                             **kwargs)
            signals.cart_content_changed.send(sender=type(self), instance=self)
        return QuantityResult(item, quantity, quantity - old_qty, reason)

    def get_item(self, **kwargs):
        return self.items.get(**kwargs)

    def get_all_items(self):
        return list(self.items.all())

    def replace_item(self, variant, quantity, dry_run=False, **kwargs):
        variant = variant.get_subtype_instance()
        quantity = variant.product.quantize_quantity(quantity)
        result = []
        reason = u""
        try:
            item = self.get_item(variant=variant, **kwargs)
            old_qty = item.quantity
        except ObjectDoesNotExist:
            item = None
            old_qty = Decimal(0)
        signals.cart_quantity_change_check.send(sender=type(self),
                                                instance=self,
                                                variant=variant,
                                                old_quantity=old_qty,
                                                new_quantity=quantity,
                                                result=result,
                                                **kwargs)
        assert len(result) <= 1
        if len(result) == 1:
            quantity, reason = result[0]
        if not dry_run:
            if not quantity:
                if item:
                    item.delete()
            else:
                if item:
                    item.quantity = quantity
                    item.save()
                else:
                    item = self.items.create(variant=variant, quantity=quantity,
                                             **kwargs)
            signals.cart_content_changed.send(sender=type(self), instance=self)
        return QuantityResult(item, quantity, quantity - old_qty, reason)

    def get_quantity(self, variant, **kwargs):
        try:
            return self.get_item(variant=variant, **kwargs).quantity
        except ObjectDoesNotExist:
            return Decimal('0')

    def is_empty(self):
        return not self.items.exists()

    def get_total(self):
        from ..pricing import Price
        return sum([i.get_price() for i in self.get_all_items()],
                   Price(0, currency=self.currency))


class CartItem(models.Model):

    cart = DeferredForeignKey('cart', related_name='items', editable=False)
    variant = DeferredForeignKey('variant', related_name='+', editable=False)
    quantity = models.DecimalField(_("quantity"), max_digits=10,
                                   decimal_places=4)

    class Meta:
        abstract = True
        unique_together = ('cart', 'variant')

    def __unicode__(self):
        return u"%s × %.10g" % (self.variant, self.quantity)

    def save(self, *args, **kwargs):
        assert self.quantity > 0
        super(CartItem, self).save(*args, **kwargs)

    def get_unit_price(self, currency=None, **kwargs):
        from ..pricing.handler import pricing_queue
        variant = self.variant.get_subtype_instance()
        currency = currency or self.cart.currency
        return pricing_queue.get_variant_price(variant, currency,
                quantity=self.quantity, cart=self.cart, cartitem=self, **kwargs)

    def get_price(self, currency=None, **kwargs):
        return self.get_unit_price(currency=currency, **kwargs) * self.quantity