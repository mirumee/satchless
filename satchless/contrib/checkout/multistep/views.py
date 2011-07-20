# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..common.decorators import require_order
from ....order import forms
from ....order import handler

@require_order(status='checkout')
def checkout(request, order_token, billing_form_class=forms.BillingForm):
    """
    Checkout step 1
    The order is split into delivery groups. User chooses delivery method
    for each of the groups.
    """
    order = request.order
    billing_form = billing_form_class(request.POST or None, instance=order)
    delivery_formset = forms.DeliveryMethodFormset(
            data=request.POST or None, queryset=order.groups.all())
    if request.method == 'POST':
        if all([billing_form.is_valid(), delivery_formset.is_valid()]):
            order = billing_form.save()
            delivery_formset.save()
            return redirect('satchless-checkout-delivery-details',
                            order_token=order.token)
    return TemplateResponse(request, 'satchless/checkout/checkout.html', {
        'billing_form': billing_form,
        'delivery_formset': delivery_formset,
        'order': order,
    })

@require_order(status='checkout')
def delivery_details(request, order_token):
    """
    Checkout step 1½
    If there are any delivery details needed (e.g. the shipping address),
    user will be asked for them. Otherwise we redirect to step 2.
    """
    order = request.order
    groups = order.groups.all()
    if filter(lambda g: not g.delivery_type, groups):
        return redirect('satchless-checkout', order_token=order.token)
    delivery_group_forms = forms.get_delivery_details_forms_for_groups(order.groups.all(),
                                                                       request.POST)
    groups_with_forms = filter(lambda gf: gf[2], delivery_group_forms)
    if len(groups_with_forms) == 0:
        # all forms are None, no details needed
        return redirect('satchless-checkout-payment-choice',
                        order_token=order.token)
    if request.method == 'POST':
        are_valid = True
        for group, typ, form in delivery_group_forms:
            are_valid = are_valid and form.is_valid()
        if are_valid:
            for group, typ, form in delivery_group_forms:
                handler.create_delivery_variant(group, form)
            return redirect('satchless-checkout-payment-choice',
                            order_token=order.token)
    return TemplateResponse(request, 'satchless/checkout/delivery_details.html', {
        'delivery_group_forms': groups_with_forms,
        'order': order,
    })

@require_order(status='checkout')
def payment_choice(request, order_token):
    """
    Checkout step 2
    User will choose the payment method.
    """
    order = request.order
    payment_form = forms.PaymentMethodForm(data=request.POST or None,
                                           instance=order)
    if request.method == 'POST':
        if payment_form.is_valid():
            payment_form.save()
            return redirect('satchless-checkout-payment-details',
                            order_token=order.token)
    return TemplateResponse(request, 'satchless/checkout/payment_choice.html', {
        'order': order,
        'payment_form': payment_form,
    })

@require_order(status='checkout')
def payment_details(request, order_token):
    """
    Checkout step 2½
    If any payment details are needed, user will be asked for them. Otherwise
    we redirect to step 3.
    """
    order = request.order
    if not order.payment_type:
        return redirect('satchless-checkout-payment-choice',
                        order_token=order.token)
    form = forms.get_payment_details_form(order, request.POST)
    def proceed(order, form):
        variant = handler.create_payment_variant(order, form)
        order.payment_variant = variant
        order.set_status('payment-pending')
        return redirect('satchless-checkout-confirmation',
                        order_token=order.token)
    if form:
        if request.method == 'POST':
            if form.is_valid():
                return proceed(order, form)
        return TemplateResponse(request, 'satchless/checkout/payment_details.html', {
            'form': form,
            'order': order,
        })
    else:
        return proceed(order, form)
