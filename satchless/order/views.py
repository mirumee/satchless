# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from satchless.cart.models import Cart

from . import models
from . import forms
from . import handler

@login_required
def my_orders(request):
    orders = models.Order.objects.filter(user=request.user)
    return direct_to_template(request, 'satchless/order/my_orders.html',
            {'orders': orders})

def view(request, order_pk):
    if request.user.is_authenticated():
        orders = models.Order.objects.filter(user=request.user)
    elif request.session.has_key('satchless_order'):
        # We allow anonymous users to see their latest order.
        orders = models.Order.objects.filter(pk=request.session['satchless_order'])
    else:
        return HttpResponseNotFound()
    try:
        order = orders.get(pk=order_pk)
    except models.Order.DoesnotExist:
        return HttpResponseNotFound()
    return direct_to_template(request, 'satchless/order/view.html',
            {'order': order})

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
        delivery_formset = None
    if order:
        delivery_formset = forms.DeliveryMethodFormset(
                data=request.POST or None, queryset=order.groups.all(),
                session=request.session)
        if request.method == 'POST':
            if delivery_formset.is_valid():
                delivery_formset.save(session=request.session)
                return redirect('satchless-checkout-delivery_details')
    return direct_to_template(request, 'satchless/order/checkout.html',
            {'order': order, 'delivery_formset': delivery_formset})

def delivery_details(request):
    """
    Checkout step 1½
    If there are any delivery details needed (e.g. the shipping address),
    user will be asked for them. Otherwise we redirect to step 2.
    """
    order = models.Order.objects.get_from_session(request.session)
    if not order:
        return redirect('satchless-checkout')
    delivery_groups_forms = forms.get_delivery_details_forms_for_groups(order, request)
    groups_with_forms = filter(lambda gf: gf[2], delivery_groups_forms)
    if len(groups_with_forms) == 0:
        # all forms are None, no details needed
        return redirect('satchless-checkout-payment_choice')
    if request.method == 'POST':
        are_valid = True
        for group, typ, form in delivery_groups_forms:
            are_valid = are_valid and form.is_valid()
        if are_valid:
            for group, typ, form in delivery_groups_forms:
                variant = handler.get_delivery_variant(group, typ, form)
            return redirect('satchless-checkout-payment_choice')
    return direct_to_template(request, 'satchless/order/delivery_details.html',
            {'order': order, 'delivery_groups_forms': groups_with_forms})

def payment_choice(request):
    """
    Checkout step 2
    User will choose the payment method.
    """
    order = models.Order.objects.get_from_session(request.session)
    if not order:
        return redirect('satchless-checkout')
    payment_form = forms.PaymentMethodForm(data=request.POST or None, instance=order)
    if request.method == 'POST':
        if payment_form.is_valid():
            payment_form.save(request.session)
            return redirect('satchless-checkout-payment_details')
    return direct_to_template(request, 'satchless/order/payment_choice.html',
            {'order': order, 'payment_form': payment_form})

def payment_details(request):
    """
    Checkout step 2½
    If any payment details are needed, user will be asked for them. Otherwise
    we redirect to step 3.
    """
    order = models.Order.objects.get_from_session(request.session)
    if not order:
        return redirect('satchless-checkout')
    form = forms.get_payment_details_form(order, request)
    typ = request.session['satchless_payment_method']

    def proceed(order, typ, form):
        variant = handler.get_payment_variant(order, typ, form)
        order.payment_variant = variant
        order.save()
        return redirect('satchless-checkout-confirmation')

    if form:
        if request.method == 'POST':
            if form.is_valid():
                return proceed(order, typ, form)
        return direct_to_template(request, 'satchless/order/payment_details.html',
                {'order': order, 'form': form})
    else:
        return proceed(order, typ, form)

def confirmation(request):
    """
    Checkout step 3
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
