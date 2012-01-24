from django.db import models
import satchless.cart.models

import products.models

class Wishlist(satchless.cart.models.Cart):

    def add_item(self, variant, quantity):
        return self.replace_item(variant, 1)

    def replace_item(self, variant, quantity, **kwargs):
        if quantity > 0:
            wishlist_item, created = self.items.get_or_create(variant=variant)
            quantity = 1
            if created:
                quantity_delta = 1
            else:
                quantity_delta = 0
        else:
            try:
                wishlist_item = self.items.get(variant=variant)
                wishlist_item.delete()
                quantity = 0
                quantity_delta = -1
            except WishlistItem.DoesNotExist:
                wishlist_item = None
                quantity = 0
                quantity_delta = 0
        return satchless.cart.models.QuantityResult(wishlist_item, quantity, quantity_delta)

    def is_empty(self):
        return not self.items.exists()


class WishlistItem(models.Model):

    cart = models.ForeignKey(Wishlist, editable=False, related_name='items')
    variant = models.ForeignKey(products.models.Variant,
                                editable=False, related_name='+')

    class Meta:
        unique_together = ('cart', 'variant')
