from django.db.models.fields.related import ForeignKey
from satchless.cart.models import Cart, CartItem

class DemoCart(Cart):

    class Meta:
        proxy = True

    def get_cart_item_class(self):
        return DemoCartItem

class DemoCartItem(CartItem):
    cart = ForeignKey(DemoCart, related_name='items')
