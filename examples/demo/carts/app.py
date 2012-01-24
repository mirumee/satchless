from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import satchless.cart.app

from categories.app import product_app

from . import handler
from . import models

class CartApp(satchless.cart.app.MagicCartApp):
    AddToCartHandler = handler.AddToCartHandler

cart_app = CartApp(product_app)


class WishlistApp(satchless.cart.app.MagicCartApp):
    app_name = 'wishlist'
    namespace = 'wishlist'
    cart_type = 'wishlist'
    Cart = models.Wishlist
    CartItem = models.WishlistItem
    AddToCartHandler = handler.AddToWishlistHandler

    def __init__(self, cart_app, *args, **kwargs):
        self.cart_app = cart_app
        super(WishlistApp, self).__init__(*args, **kwargs)

    def add_to_cart(self, request, wishlist_item_id):
        wishlist = self.get_cart_for_request(request)
        try:
            item = wishlist.get_item(id=wishlist_item_id)
        except ObjectDoesNotExist:
            raise Http404()
        cart = self.cart_app.get_cart_for_request(request)
        cart.add_item(variant=item.variant, quantity=1)
        return self.cart_app.redirect('details')

    def get_urls(self):
        parent_urls = super(WishlistApp, self).get_urls()
        return parent_urls + patterns('',
            url(r'^add-to-cart/(?P<wishlist_item_id>\d+)/$', self.add_to_cart,
                name='add-to-cart'),
        )

wishlist_app = WishlistApp(cart_app=cart_app, product_app=product_app)
