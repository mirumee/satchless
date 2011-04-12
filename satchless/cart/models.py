# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ..product.models import Variant

from . import signals

CART_SESSION_KEY = '_satchless_cart-%s' # takes typ

def get_default_currency():
    return settings.SATCHLESS_DEFAULT_CURRENCY

class CartManager(models.Manager):
    def get_or_create_from_request(self, request, typ):
        try:
            cart = self.get(typ=typ, pk=request.session[CART_SESSION_KEY % typ])
            if cart.owner is None and request.user.is_authenticated():
                cart.owner = request.user
                cart.save()
            return cart
        except (Cart.DoesNotExist, KeyError):
            owner = request.user if request.user.is_authenticated() else None
            cart = self.create(typ=typ, owner=owner)
            request.session[CART_SESSION_KEY % typ] = cart.pk
            return cart


class Cart(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    typ = models.CharField(_("type"), max_length=100)
    currency = models.CharField(_("currency"), max_length=3,
                                default=get_default_currency)

    objects = CartManager()

    def add_quantity(self, variant, quantity, dry_run=False):
        variant = variant.get_subtype_instance()
        quantity = variant.product.sanitize_quantity(quantity)
        try:
            item = self.items.get(variant=variant)
            old_qty = item.quantity
        except CartItem.DoesNotExist:
            item = CartItem(cart=self, variant=variant)
            old_qty = Decimal('0')
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
        return (new_qty, new_qty - old_qty, reason)

    def set_quantity(self, variant, quantity, dry_run=False):
        variant = variant.get_subtype_instance()
        quantity = variant.product.sanitize_quantity(quantity)
        try:
            item = self.items.get(variant=variant)
            old_qty = item.quantity
        except CartItem.DoesNotExist:
            item = CartItem(cart=self, variant=variant)
            old_qty = Decimal('0')
        result = []
        reason = u""
        signals.cart_quantity_change_check.send(sender=type(self),
                                                instance=self,
                                                variant=variant,
                                                old_quantity=old_qty,
                                                new_quantity=quantity,
                                                result=result)
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
        return (quantity, reason)

    def get_quantity(self, variant):
        try:
            return self.items.get(variant=variant).quantity
        except CartItem.DoesNotExist:
            return Decimal('0')

    def is_empty(self):
        return self.items.count() == 0

    def __unicode__(self):
        if self.owner:
            return u"%s of %s" % (self.typ, self.owner.username)
        else:
            return self.typ


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items')
    variant = models.ForeignKey(Variant)
    quantity = models.DecimalField(_("quantity"), max_digits=10,
                                   decimal_places=4)

    def save(self, *args, **kwargs):
        assert(self.quantity > 0)
        super(CartItem, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s × %s" % (self.variant, self.quantity)

    def get_unit_price(self, currency=None, **kwargs):
        from ..pricing import handler
        variant = self.variant.get_subtype_instance()
        currency = currency if currency else self.cart.currency
        return handler.get_variant_price(variant, currency,
                quantity=self.quantity, cart=self.cart, cartitem=self, **kwargs)

    class Meta:
        unique_together = ('cart', 'variant')
