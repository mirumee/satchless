# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic.simple import direct_to_template

from ....cart.models import Cart
from ....order import forms
from ....order import models
from ....order import handler

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
        return redirect('satchless-cart-view', typ=typ)

    delivery_groups = order.groups.all()
    for group in delivery_groups:
        delivery_types = handler.get_delivery_types(group)
        if len(delivery_types) != 1:
            raise ImproperlyConfigured("The singlestep checkout requires "
                                       "exactly one delivery type per group.")
        group.delivery_type = delivery_types[0][0]

    delivery_valid = True
    delivery_groups_forms = forms.get_delivery_details_forms_for_groups(delivery_groups, request)
    if request.method == 'POST':
        delivery_valid = True
        for group, typ, form in delivery_groups_forms:
            if form:
                delivery_valid = delivery_valid and form.is_valid()

    payment_types = handler.get_payment_types(order)
    if len(payment_types) > 1:
        raise ImproperlyConfigured("The singlestep checkout cannot handle multiple payment "
                                   "methods. Methods for this order: %s" % payment_types)
    payment_type = payment_types[0][0]
    PaymentForm = handler.get_payment_formclass(order, payment_type)
    payment_form = PaymentForm(data=request.POST or None, instance=order) if PaymentForm else None
    if request.method == 'POST':
        payment_valid = payment_form.is_valid() if payment_form else True

        if delivery_valid and payment_valid:
            for group, typ, form in delivery_groups_forms:
                handler.create_delivery_variant(group, typ, form)
            handler.create_payment_variant(order, payment_type, payment_form)
            request.session['satchless_order'] = order.pk
            request.session['satchless_payment_method'] = payment_type
            return redirect('satchless-checkout-confirmation')
    return direct_to_template(request, 'satchless/checkout/checkout.html',
            {'order': order, 'delivery_groups_forms': delivery_groups_forms,
             'payment_form': payment_form})
