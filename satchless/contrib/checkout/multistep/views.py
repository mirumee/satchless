# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..common.views import order_from_request
from ....cart.models import Cart
from ....payment import PaymentFailure, ConfirmationFormNeeded
from ....order import models
from ....order import forms
from ....order import handler
from ....order import signals

def checkout(request, typ):
    """
    Checkout step 1
    The order is split into delivery groups. User chooses delivery method
    for each of the groups.
    """
    cart = Cart.objects.get_or_create_from_request(request, typ)
    order_pk = request.session.get('satchless_order')
    order = None
    if order_pk:
        cart = Cart.objects.get_or_create_from_request(request, typ)
        try:
            order = models.Order.objects.get(pk=order_pk, cart=cart,
                                             status='checkout')
        except models.Order.DoesNotExist:
            pass
    if not order:
        return redirect('satchless-cart-view', typ=typ)
    delivery_formset = forms.DeliveryMethodFormset(
            data=request.POST or None, queryset=order.groups.all())
    if request.method == 'POST':
        if delivery_formset.is_valid():
            delivery_formset.save()
            return redirect('satchless-checkout-delivery-details')
    return TemplateResponse(request, 'satchless/checkout/checkout.html', {
        'delivery_formset': delivery_formset,
        'order': order,
    })

def delivery_details(request):
    """
    Checkout step 1½
    If there are any delivery details needed (e.g. the shipping address),
    user will be asked for them. Otherwise we redirect to step 2.
    """
    order = order_from_request(request)
    if not order:
        return redirect('satchless-cart-view')
    groups = order.groups.all()
    if filter(lambda g: not g.delivery_type, groups):
        return redirect('satchless-checkout')
    delivery_group_forms = forms.get_delivery_details_forms_for_groups(order.groups.all(), request)
    groups_with_forms = filter(lambda gf: gf[2], delivery_group_forms)
    if len(groups_with_forms) == 0:
        # all forms are None, no details needed
        return redirect('satchless-checkout-payment-choice')
    if request.method == 'POST':
        are_valid = True
        for group, typ, form in delivery_group_forms:
            are_valid = are_valid and form.is_valid()
        if are_valid:
            for group, typ, form in delivery_group_forms:
                handler.create_delivery_variant(group, form)
            return redirect('satchless-checkout-payment-choice')
    return TemplateResponse(request, 'satchless/checkout/delivery_details.html', {
        'delivery_group_forms': groups_with_forms,
        'order': order,
    })

def payment_choice(request):
    """
    Checkout step 2
    User will choose the payment method.
    """
    order = order_from_request(request)
    if not order:
        return redirect('satchless-checkout')
    payment_form = forms.PaymentMethodForm(data=request.POST or None, instance=order)
    if request.method == 'POST':
        if payment_form.is_valid():
            payment_form.save()
            return redirect('satchless-checkout-payment-details')
    return TemplateResponse(request, 'satchless/checkout/payment_choice.html', {
        'order': order,
        'payment_form': payment_form,
    })

def payment_details(request):
    """
    Checkout step 2½
    If any payment details are needed, user will be asked for them. Otherwise
    we redirect to step 3.
    """
    order = order_from_request(request)
    if not order:
        return redirect('satchless-checkout')
    if not order.payment_type:
        return redirect('satchless-checkout-payment-choice')
    form = forms.get_payment_details_form(order, request)

    def proceed(order, form):
        variant = handler.create_payment_variant(order, form)
        order.payment_variant = variant
        order.save()
        return redirect('satchless-checkout-confirmation')

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

def confirmation(request):
    """
    Checkout step 3
    The final summary, where user is asked to review and confirm the order.
    Confirmation will redirect to the payment gateway.
    """
    order = order_from_request(request)
    if not order:
        return redirect('satchless-checkout')
    order.set_status('payment-pending')
    signals.order_pre_confirm.send(sender=models.Order, instance=order, request=request)
    try:
        handler.confirm(order, request.session['satchless_payment_method'])
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
