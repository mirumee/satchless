from django.db import models

from carts.app import cart_app, wishlist_app

def carts_sizes(request):
    try:
        cart_size = (cart_app.get_cart_for_request(request)
                                 .items.aggregate(cart_size=models.Sum('quantity')))['cart_size'] or 0
    except cart_app.Cart.DoesNotExist:
        cart_size = 0
    try:
        wishlist_size = (wishlist_app.get_cart_for_request(request)
                                     .items.count()) or 0
    except wishlist_app.Cart.DoesNotExist:
        wishlist_size = 0
    return {'cart_size': cart_size,
            'wishlist_size': wishlist_size}
