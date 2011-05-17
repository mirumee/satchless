# -*- coding:utf-8 -*-
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from ....cart.models import Cart
from ....order import models


def order_from_request(request):
    '''
    Get the order from session, possibly invalidating the variable if the
    order has been processed already.
    '''
    session = request.session
    if 'satchless_order' in session:
        try:
            return models.Order.objects.get(pk=session['satchless_order'],
                                            status='checkout')
        except models.Order.DoesNotExist:
            del session['satchless_order']
    return None

@require_POST
def prepare_order(request, typ):
    cart = Cart.objects.get_or_create_from_request(request, typ)
    order_pk = request.session.get('satchless_order')
    previous_orders = models.Order.objects.filter(pk=order_pk, cart=cart,
                                                  status='checkout')
    if not order_pk or not previous_orders.exists():
        try:
            order = models.Order.objects.get_from_cart(cart)
        except models.EmptyCart:
            return redirect('satchless-cart-view', typ=typ)
        else:
            request.session['satchless_order'] = order.pk
    return redirect('satchless-checkout')

