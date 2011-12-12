from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404, redirect
import satchless.cart.app
import satchless.cart.signals

from categories.app import product_app

cart_app = satchless.cart.app.MagicCartApp(product_app)

class WishlistApp(satchless.cart.app.MagicCartApp):
    app_name = 'wishlist'
    namespace = 'wishlist'
    cart_type = 'wishlist'
    Cart = cart_app.Cart
    CartItem = cart_app.CartItem

    def add_to_cart(self, request, wishlist_item_id):
        wishlist = self.Cart.objects.get_or_create_from_request(request,
                                                           self.cart_type)
        item = get_object_or_404(wishlist.items.all(), id=wishlist_item_id)
        cart = self.Cart.objects.get_or_create_from_request(request, 'cart')
        form_result = cart.add_item(variant=item.variant, quantity=1)
        satchless.cart.signals.cart_item_added.send(sender=type(form_result.cart_item),
                                                    instance=form_result.cart_item,
                                                    result=form_result,
                                                    request=request)
        return redirect('cart:details')

    def get_urls(self):
        parent_urls = super(WishlistApp, self).get_urls()
        return parent_urls + patterns('',
            url(r'^add-to-cart/(?P<wishlist_item_id>\d+)/$', self.add_to_cart,
                name='add-to-cart'),
        )


wishlist_app = WishlistApp(product_app)
