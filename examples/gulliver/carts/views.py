# -*- coding:utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from satchless.cart.models import Cart

def from_wishlist_to_cart(request, wishlist_item_id):
    wishlist = Cart.objects.get_or_create_from_request(request, 'satchless_wishlist')
    item = get_object_or_404(wishlist.items.all(), id=wishlist_item_id)

    cart = Cart.objects.get_or_create_from_request(request, 'satchless_cart')
    cart.add_quantity(variant=item.variant, quantity=1)
    messages.success(request, _(u'Product added to cart.'))

    return HttpResponseRedirect(reverse('satchless-cart-view', args=('satchless_wishlist',)))

