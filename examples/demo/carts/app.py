from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404, redirect
from satchless.cart import app
from satchless.cart import signals
from satchless.cart.models import Cart

class WishlistApp(app.CartApp):
    app_name = 'wishlist'
    namespace = 'wishlist'
    cart_type = 'wishlist'

    def add_to_cart(self, request, wishlist_item_id):
        wishlist = Cart.objects.get_or_create_from_request(request,
                                                           self.cart_type)
        item = get_object_or_404(wishlist.items.all(), id=wishlist_item_id)
        cart = Cart.objects.get_or_create_from_request(request, 'cart')
        form_result = cart.add_quantity(variant=item.variant, quantity=1)
        signals.cart_item_added.send(sender=type(form_result.cart_item),
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


class CartApp(app.CartApp):
    app_name = 'cart'
    cart_type = 'cart'


wishlist_app = WishlistApp()
cart_app = CartApp()