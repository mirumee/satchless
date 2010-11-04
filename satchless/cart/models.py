from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from satchless.product.models import Variant

from decimal import Decimal

CART_SESSION_KEY = '_satchless_cart-%s' # takes typ

class CartManager(models.Manager):
    def get_or_create_from_request(self, request, typ):
        try:
            return self.get(typ=typ, pk=request.session[CART_SESSION_KEY % typ])
        except (Cart.DoesNotExist, KeyError):
            owner = request.user if request.user.is_authenticated() else None
            cart = self.create(typ=typ, owner=owner)
            request.session[CART_SESSION_KEY % typ] = cart.pk
            return cart


class Cart(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    typ = models.CharField(_("type"), max_length=100)

    objects = CartManager()

    def add_quantity(self, variant, quantity):
        try:
            item = self.items.get(variant=variant)
            item.quantity += quantity
            item.save()
        except CartItem.DoesNotExist:
            item = self.items.create(variant=variant, quantity=quantity)
        return item.quantity

    def set_quantity(self, variant, quantity):
        try:
            item = self.items.get(variant=variant)
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
        except CartItem.DoesNotExist:
            if quantity > 0:
                item = self.items.create(variant=variant, quantity=quantity)

    def get_quantity(self, variant):
        try:
            return self.items.get(variant=variant).quantity
        except CartItem.DoesNotExist:
            return Decimal('0')

    def __unicode__(self):
        if self.owner:
            return u"%s of %s" % (self.typ, self.user.username)
        else:
            return self.typ


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items')
    variant = models.ForeignKey(Variant)
    quantity = models.DecimalField(_("quantity"), max_digits=10, decimal_places=4)

    def __unicode__(self):
        return u"%s x %s" % (self.variant, self.quantity)

    class Meta:
        unique_together = ('cart', 'variant')
