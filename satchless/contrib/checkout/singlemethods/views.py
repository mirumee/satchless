# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template

from ....cart.models import Cart
from ....order import models
from ....order import handler

@require_POST
def order_from_cart(request, typ):
    cart = Cart.objects.get_or_create_from_request(request, typ)
    order_pk = request.session.get('satchless_order')
    if not order_pk or not models.Order.objects.filter(pk=order_pk, cart=cart, status='checkout').exists():
        try:
            order = models.Order.objects.get_from_cart(cart)
            request.session['satchless_order'] = order.pk
        except models.EmptyCart:
            return HttpResponseRedirect(reverse('satchless-cart-view', args=(typ,)))
    return HttpResponseRedirect(reverse('satchless-checkout'))

def checkout(request, typ):
    """
    Checkout step 1
    The order is split into delivery groups. User chooses delivery method
    for each of the groups.
    """
    order_pk = request.session.get('satchless_order')
    order = None
    if order_pk:
        try:
            cart = Cart.objects.get_or_create_from_request(request, typ)
            order = models.Order.objects.get(pk=order_pk, cart=cart, status='checkout')
        except models.Order.DoesNotExist:
            pass
    if not order:
        return HttpResponseRedirect(reverse('satchless-cart-view', args=(typ,)))

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
    try:
        dvariant = dgroup.deliveryvariant
    except ObjectDoesNotExist:
        dvariant = None
    if DeliveryForm:
        dform = DeliveryForm(data=request.POST or None, instance=dvariant, prefix='delivery_details')
    else:
        dform = None
    ptypes = handler.get_payment_types(order)
    if len(ptypes) > 1:
        raise ValueError("The singlemethods checkout cannot handle multiple payment "
                "methods. Methods for this order: %s" % ptypes)
    ptyp = ptypes[0][0]
    PaymentForm = handler.get_payment_formclass(order, ptyp)
    if PaymentForm:
        pform = PaymentForm(data=request.POST or None, instance=order)
    else:
        pform = None
    if request.method == 'POST' or (pform is None and dform is None):
        dvalid = dform.is_valid() if dform else True
        pvalid = pform.is_valid() if pform else True
        if dvalid and pvalid:
            dvariant = handler.get_delivery_variant(dgroup, dtyp, dform)
            pvariant = handler.get_payment_variant(order, ptyp, pform)
            request.session['satchless_order'] = order.pk
            request.session['satchless_payment_method'] = ptyp
            return redirect('satchless-checkout-confirmation')
    return direct_to_template(request, 'satchless/checkout/checkout.html',
            {'order': order, 'delivery_form': dform, 'payment_form': pform})
