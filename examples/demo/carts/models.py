from django.db import models
import satchless.cart.models
from satchless.item import ItemLine
from satchless.util.models import construct

import products.models


class Cart(satchless.cart.models.Cart):
    pass


class CartItem(construct(satchless.cart.models.CartItem, cart=Cart,
                         variant=products.models.Variant)):

    def get_price_per_item(self, quantity=1, **kwargs):
        variant = self.variant.get_subtype_instance()
        if variant.product.qty_mode == 'product':
            for i in self.cart:
                ov = i.variant.get_subtype_instance()
                if not ov == variant and ov.product == variant.product:
                    quantity += i.get_quantity()
        return variant.get_price(quantity=quantity, **kwargs)


class Wishlist(satchless.cart.models.Cart):

    def add_item(self, variant, quantity):
        return self.replace_item(variant, 1)

    def replace_item(self, variant, quantity, **kwargs):
        try:
            wishlist_item = self.items.get(variant=variant)
        except WishlistItem.DoesNotExist:
            old_quantity = 0
            wishlist_item = None
        else:
            old_quantity = 1

        if quantity > 0 and not wishlist_item:
            wishlist_item = self.items.create(variant=variant)
        elif quantity == 0 and wishlist_item:
            wishlist_item.delete()
        quantity = 1 if quantity else 0
        return satchless.cart.models.QuantityResult(wishlist_item, quantity,
                                                    quantity - old_quantity)

    def is_empty(self):
        return not self.items.exists()


class WishlistItem(models.Model, ItemLine):

    cart = models.ForeignKey(Wishlist, editable=False, related_name='items')
    variant = models.ForeignKey(products.models.Variant,
                                editable=False, related_name='+')

    class Meta:
        unique_together = ('cart', 'variant')

    def get_price_per_item(self, **kwargs):
        return self.variant.get_subtype_instance().get_price(**kwargs)

    def get_quantity(self, **kwargs):
        return 1
