# -*- coding:utf-8 -*-
from django.shortcuts import get_object_or_404, redirect

from satchless.cart.models import Cart
from satchless.cart import signals

def from_wishlist_to_cart(request, wishlist_item_id):
    wishlist = Cart.objects.get_or_create_from_request(request,
                                                       'satchless_wishlist')
    item = get_object_or_404(wishlist.items.all(), id=wishlist_item_id)
    cart = Cart.objects.get_or_create_from_request(request, 'satchless_cart')
    form_result = cart.add_quantity(variant=item.variant, quantity=1)
    signals.cart_item_added.send(sender=type(form_result.cart_item),
                                 instance=form_result.cart_item,
                                 result=form_result,
                                 request=request)
    return redirect('satchless-cart-view', typ='satchless_wishlist')
