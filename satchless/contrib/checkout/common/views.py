# -*- coding:utf-8 -*-
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ....cart.models import Cart
from ....order import handler
from ....order import models
from ....order import signals
from ....payment import PaymentFailure, ConfirmationFormNeeded

from .decorators import require_order

@require_POST
def prepare_order(request, typ):
    cart = Cart.objects.get_or_create_from_request(request, typ)
    order_pk = request.session.get('satchless_order')
    previous_orders = models.Order.objects.filter(pk=order_pk, cart=cart,
                                                  status='checkout')
    try:
        order = previous_orders.get()
    except models.Order.DoesNotExist:
        try:
            order = models.Order.objects.get_from_cart(cart)
        except models.EmptyCart:
            return redirect('satchless-cart-view')
    request.session['satchless_order'] = order.pk
    return redirect('satchless-checkout', order_token=order.token)

@require_POST
@require_order(status='payment-failed')
def reactivate_order(request, order_token):
    order = request.order
    order.set_status('checkout')
    return redirect('satchless-checkout', order_token=order.token)

@require_order(status='payment-pending')
def confirmation(request, order_token):
    """
    Checkout confirmation
    The final summary, where user is asked to review and confirm the order.
    Confirmation will redirect to the payment gateway.
    """
    order = request.order
    if not request.order:
        return redirect('satchless-checkout', order_token=order.token)
    signals.order_pre_confirm.send(sender=models.Order, instance=order,
                                   request=request)
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
    return redirect('satchless-order-view', order_token=order.token)
