from django.db import models
from models import DemoCart

from satchless.cart.models import Cart

def carts_sizes(request):
    try:
        cart_size = (DemoCart.objects.get_from_request(request, 'cart')
                                 .items.aggregate(cart_size=models.Sum('quantity')))['cart_size'] or 0
    except Cart.DoesNotExist:
        cart_size = 0
    try:
        wishlist_size = (DemoCart.objects.get_from_request(request, 'wishlist')
                                     .items.aggregate(cart_size=models.Sum('quantity')))['cart_size'] or 0
    except Cart.DoesNotExist:
        wishlist_size = 0
    return {'cart_size': cart_size,
            'wishlist_size': wishlist_size}