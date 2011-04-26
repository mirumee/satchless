# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from ....cart.models import Cart
from ....order import models
from ....order import handler

def checkout(request, typ):
    """
    Checkout step 1
    The order is split into delivery groups. User chooses delivery method
    for each of the groups.
    """
    cart = Cart.objects.get_or_create_from_request(request, typ)
    try:
        order = models.Order.objects.create_for_cart(cart, session=request.session)
    except models.EmptyCart:
        order = None
    if order:
        if order.groups.count() > 1:
            raise ValueError("The singlemethods checkout cannot handle multiple delivery "
                    "groups. Groups in this order: %s" % order.groups.all())
        dgroup = order.groups.all()[0]
        dtypes = handler.get_delivery_types(dgroup)
        if len(dtypes) > 1:
            raise ValueError("The singlemethods checkout cannot handle multiple delivery "
                    "methods. Methods for this order: %s" % dtypes)
        dtyp = dtypes[0][0]
        DeliveryForm = handler.get_delivery_formclass(dgroup, dtyp)
        dform = DeliveryForm(data=request.POST or None, prefix='delivery_details')
        ptypes = handler.get_payment_types(order)
        if len(ptypes) > 1:
            raise ValueError("The singlemethods checkout cannot handle multiple payment "
                    "methods. Methods for this order: %s" % ptypes)
        ptyp = ptypes[0][0]
        PaymentForm = handler.get_payment_formclass(order, ptyp)
        pform = PaymentForm(data=request.POST or None, instance=order)
        if request.method == 'POST':
            if dform.is_valid() and pform.is_valid():
                dvariant = handler.get_delivery_variant(dgroup, dtyp, dform)
                pvariant = handler.get_payment_variant(order, ptyp, pform)
                return redirect('satchless-checkout-confirmation')
    return direct_to_template(request, 'satchless/checkout/checkout.html',
            {'order': order, 'delivery_form': dform, 'payment_form': pform})

def confirmation(request):
    """
    Checkout step 2 of 2
    The final summary, where user is asked to review and confirm the order.
    Confirmation will redirect to the payment gateway.
    """
    order = models.Order.objects.get_from_session(request.session)
    if not order:
        return redirect('satchless-checkout')
    order.set_status('payment-pending')
    # TODO: get rid of typ here. We have the variant already.
    formdata = handler.get_confirmation_formdata(order, request.session['satchless_payment_method'])
    return direct_to_template(request, 'satchless/order/confirmation.html',
            {'order': order, 'formdata': formdata})
