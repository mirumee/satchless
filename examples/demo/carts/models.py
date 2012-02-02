from django.db import models
import satchless.cart.models

import products.models

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
                                                    quantity-old_quantity)

    def is_empty(self):
        return not self.items.exists()


class WishlistItem(models.Model):

    cart = models.ForeignKey(Wishlist, editable=False, related_name='items')
    variant = models.ForeignKey(products.models.Variant,
                                editable=False, related_name='+')

    class Meta:
        unique_together = ('cart', 'variant')
