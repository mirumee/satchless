# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from ..product.models import Variant

from . import signals

CART_SESSION_KEY = '_satchless_cart-%s' # takes typ

def get_default_currency():
    return settings.SATCHLESS_DEFAULT_CURRENCY

class CartManager(models.Manager):
    def get_from_request(self, request, typ):
        try:
            cart = self.get(typ=typ, pk=request.session[CART_SESSION_KEY % typ])
            if cart.owner is None and request.user.is_authenticated():
                cart.owner = request.user
                cart.save()
        except (self.model.DoesNotExist, KeyError):
            raise self.model.DoesNotExist()
        return cart

    def get_or_create_from_request(self, request, typ):
        try:
            return self.get_from_request(request, typ)
        except (self.model.DoesNotExist, KeyError):
            owner = request.user if request.user.is_authenticated() else None
            cart = self.create(typ=typ, owner=owner)
            request.session[CART_SESSION_KEY % typ] = cart.pk
            return cart

class QuantityResult(object):
    def __init__(self, cart_item, new_quantity, quantity_delta, reason=None):
        self.cart_item = cart_item
        self.new_quantity = new_quantity
        self.quantity_delta =  quantity_delta
        self.reason = reason

class Cart(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, related_name='carts')
    typ = models.CharField(_("type"), max_length=100)
    currency = models.CharField(_("currency"), max_length=3,
                                default=get_default_currency)

    objects = CartManager()

    def __unicode__(self):
        if self.owner:
            return u"%s of %s" % (self.typ, self.owner.username)
        else:
            return self.typ

    def add_item(self, variant, quantity, dry_run=False, **kwargs):
        variant = variant.get_subtype_instance()
        quantity = variant.product.sanitize_quantity(quantity)
        item, old_qty = self.create_or_update_cart_item(variant, **kwargs)
        new_qty = old_qty + quantity
        result = []
        reason = u""
        signals.cart_quantity_change_check.send(sender=type(self),
                                                instance=self,
                                                variant=variant,
                                                old_quantity=old_qty,
                                                new_quantity=new_qty,
                                                result=result)
        assert(len(result) <= 1)
        if len(result) == 1:
            new_qty, reason = result[0]
        if not dry_run:
            if new_qty == 0:
                if item.pk:
                    item.delete()
            else:
                item.quantity = new_qty
                item.save()
            signals.cart_content_changed.send(sender=type(self), instance=self)
        return QuantityResult(item, new_qty, new_qty - old_qty, reason)

    def get_cart_item_class(self):
        raise NotImplementedError("Must return a subclass of CartItem")

    def get_item(self, variant, **kwargs):
        cart_item_class = self.get_cart_item_class()
        return cart_item_class.objects.get(cart=self, variant=variant, **kwargs)

    def get_all_items(self):
        cart_item_class = self.get_cart_item_class()
        return cart_item_class.objects.filter(cart=self)

    def create_or_update_cart_item(self, variant, **kwargs):
        cart_item_class = self.get_cart_item_class()
        try:
            item = self.get_item(variant, **kwargs)
            old_qty = item.quantity
        except ObjectDoesNotExist:
            item = cart_item_class(cart=self, variant=variant, **kwargs)
            old_qty = Decimal('0')
        return (item, old_qty)

    def replace_item(self, variant, quantity, dry_run=False, **kwargs):
        variant = variant.get_subtype_instance()
        quantity = variant.product.sanitize_quantity(quantity)
        item, old_qty = self.create_or_update_cart_item(variant, **kwargs)
        result = []
        reason = u""
        signals.cart_quantity_change_check.send(sender=type(self),
                                                instance=self,
                                                variant=variant,
                                                old_quantity=old_qty,
                                                new_quantity=quantity,
                                                result=result,
                                                **kwargs)
        assert(len(result) <= 1)
        if len(result) == 1:
            quantity, reason = result[0]
        if not dry_run:
            if quantity == 0:
                if item.pk:
                    item.delete()
            else:
                item.quantity = quantity
                item.save()
            signals.cart_content_changed.send(sender=type(self), instance=self)
        return QuantityResult(item, quantity, quantity - old_qty, reason)

    def get_quantity(self, variant, **kwargs):
        cart_item_class = self.get_cart_item_class()
        try:
            return self.get_item(variant=variant, **kwargs).quantity
        except cart_item_class.DoesNotExist:
            return Decimal('0')

    def is_empty(self):
        return self.get_all_items().count() == 0

    def total(self):
        from ..pricing import Price
        return sum([i.price() for i in self.get_all_items().all()],
                   Price(0, currency=self.currency))
    
    class Meta:
        abstract = True

class CartItem(models.Model):

    variant = models.ForeignKey(Variant, related_name='+')
    quantity = models.DecimalField(_("quantity"), max_digits=10,
                                   decimal_places=4)

    class Meta:
        abstract = True
        unique_together = ('cart', 'variant')

    def __unicode__(self):
        return u"%s × %.10g" % (self.variant, self.quantity)

    def save(self, *args, **kwargs):
        assert(self.quantity > 0)
        super(CartItem, self).save(*args, **kwargs)

    def get_unit_price(self, currency=None, **kwargs):
        from ..pricing.handler import pricing_queue
        variant = self.variant.get_subtype_instance()
        currency = currency or self.cart.currency
        return pricing_queue.get_variant_price(variant, currency,
                quantity=self.quantity, cart=self.cart, cartitem=self, **kwargs)

    def price(self, currency=None, **kwargs):
        return self.get_unit_price(currency=currency, **kwargs) * self.quantity