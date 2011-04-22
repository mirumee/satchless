from satchless.cart.handler import AddToCartHandler

from . import forms

add_to_cart_handler = AddToCartHandler('satchless_cart',
                                  addtocart_formclass=forms.AddToCartForm)

add_to_wishlist_handler = AddToCartHandler('satchless_wishlist',
                                      addtocart_formclass=forms.AddToWishlistForm)

def carts_handler(instances=None, request=None, extra_context=None, **kwargs):
    if request.method == 'POST' and 'satchless_wishlist' in request.POST:
        return add_to_wishlist_handler(instances, request, extra_context, **kwargs)
    return add_to_cart_handler(instances, request, extra_context, **kwargs)
