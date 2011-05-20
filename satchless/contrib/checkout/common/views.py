# -*- coding:utf-8 -*-
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ....cart.models import Cart
from ....order import handler
from ....order import models
from ....order import signals
from ....payment import PaymentFailure, ConfirmationFormNeeded


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

def confirmation(request):
    """
    Checkout confirmation
    The final summary, where user is asked to review and confirm the order.
    Confirmation will redirect to the payment gateway.
    """
    order = order_from_request(request)
    if not order:
        return redirect('satchless-checkout')
    order.set_status('payment-pending')
    signals.order_pre_confirm.send(sender=models.Order, instance=order, request=request)
    try:
        handler.confirm(order)
    except ConfirmationFormNeeded, e:
        return TemplateResponse(request, 'satchless/checkout/confirmation.html', {
            'formdata': e,
            'order': order,
        })
    except PaymentFailure:
        order.set_status('payment-failed')
    else:
        order.set_status('payment-complete')
    return redirect('satchless-order-view', order.pk)
