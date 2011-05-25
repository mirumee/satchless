# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..common.views import order_from_request
from ....order import forms
from ....order import handler

def checkout(request, typ):
    """
    Checkout step 1
    The order is split into delivery groups. User chooses delivery method
    for each of the groups.
    """
    order = order_from_request(request)
    if not order:
        return redirect('satchless-cart-view', typ=typ)

    delivery_groups = order.groups.all()
    for group in delivery_groups:
        delivery_types = handler.get_delivery_types(group)
        if len(delivery_types) != 1:
            raise ImproperlyConfigured("The singlestep checkout requires "
                                       "exactly one delivery type per group.")
        group.delivery_type = delivery_types[0][0]
        group.save()

    delivery_group_forms = forms.get_delivery_details_forms_for_groups(delivery_groups,
                                                                       request.POST)
    delivery_valid = True
    if request.method == 'POST':
        delivery_valid = True
        for group, typ, form in delivery_group_forms:
            if form:
                delivery_valid = delivery_valid and form.is_valid()

    payment_types = handler.get_payment_types(order)
    if len(payment_types) > 1:
        raise ImproperlyConfigured("The singlestep checkout cannot handle multiple payment "
                                   "methods. Methods for this order: %s" % payment_types)
    order.payment_type = payment_types[0][0]
    order.save()
    payment_form = forms.get_payment_details_form(order, request.POST)
    if request.method == 'POST':
        payment_valid = payment_form.is_valid() if payment_form else True

        if delivery_valid and payment_valid:
            for group, typ, form in delivery_group_forms:
                handler.create_delivery_variant(group, form)
            handler.create_payment_variant(order, payment_form)
            order.set_status('payment-pending')
            return redirect('satchless-checkout-confirmation')
    return TemplateResponse(request, 'satchless/checkout/checkout.html', {
        'delivery_group_forms': delivery_group_forms,
        'order': order,
        'payment_form': payment_form,
    })
