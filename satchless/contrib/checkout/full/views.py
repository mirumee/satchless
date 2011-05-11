# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_POST

from ....cart.models import Cart
from ....payment import PaymentFailure, ConfirmationFormNeeded
from ....order import models
from ....order import forms
from ....order import handler
from ....order import signals

def _order_from_request(request):
    '''
    Get the order from session, possibly invalidating the variable if the
    order has been processed already.
    '''
    session = request.session
    try:
        order = models.Order.objects.get(pk=session['satchless_order'], status='checkout')
        return order
    except KeyError:
        return None
    except models.Order.DoesNotExist:
        del session['satchless_order']
        return None

@require_POST
def prepare_order(request, typ):
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
    cart = Cart.objects.get_or_create_from_request(request, typ)
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

    delivery_formset = forms.DeliveryMethodFormset(
            data=request.POST or None, queryset=order.groups.all(),
            session=request.session)
    if request.method == 'POST':
        if delivery_formset.is_valid():
            delivery_formset.save(session=request.session)
            return redirect('satchless-checkout-delivery_details')
    return direct_to_template(request, 'satchless/checkout/checkout.html',
            {'order': order, 'delivery_formset': delivery_formset})

def delivery_details(request):
    """
    Checkout step 1½
    If there are any delivery details needed (e.g. the shipping address),
    user will be asked for them. Otherwise we redirect to step 2.
    """
    order = _order_from_request(request)
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
    return direct_to_template(request, 'satchless/checkout/delivery_details.html',
            {'order': order, 'delivery_groups_forms': groups_with_forms})

def payment_choice(request):
    """
    Checkout step 2
    User will choose the payment method.
    """
    order = _order_from_request(request)
    if not order:
        return redirect('satchless-checkout')
    payment_form = forms.PaymentMethodForm(data=request.POST or None, instance=order)
    if request.method == 'POST':
        if payment_form.is_valid():
            payment_form.save(request.session)
            return redirect('satchless-checkout-payment_details')
    return direct_to_template(request, 'satchless/checkout/payment_choice.html',
            {'order': order, 'payment_form': payment_form})

def payment_details(request):
    """
    Checkout step 2½
    If any payment details are needed, user will be asked for them. Otherwise
    we redirect to step 3.
    """
    order = _order_from_request(request)
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
        return direct_to_template(request, 'satchless/checkout/payment_details.html',
                {'order': order, 'form': form})
    else:
        return proceed(order, typ, form)

def confirmation(request):
    """
    Checkout step 3
    The final summary, where user is asked to review and confirm the order.
    Confirmation will redirect to the payment gateway.
    """
    order = _order_from_request(request)
    if not order:
        return redirect('satchless-checkout')
    order.set_status('payment-pending')
    signals.order_pre_confirm.send(sender=models.Order, instance=order, request=request)
    try:
        handler.confirm(order, request.session['satchless_payment_method'])
    except ConfirmationFormNeeded, e:
        return direct_to_template(request, 'satchless/checkout/confirmation.html',
            {'order': order, 'formdata': e})
    except PaymentFailure:
        order.set_status('payment-failed')
    else:
        order.set_status('payment-complete')
    return redirect('satchless-order-view', order.pk)
