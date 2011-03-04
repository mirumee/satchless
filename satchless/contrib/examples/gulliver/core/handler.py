from satchless.cart.handler import AddToCartHandler

from . import forms

cart_handler = AddToCartHandler('satchless_cart',
                                addtocart_formclass=forms.AddToCartForm)
