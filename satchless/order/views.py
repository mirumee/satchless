from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from satchless.cart.models import Cart

from . import models
from . import forms

def checkout(request, typ):
    cart = Cart.objects.get_or_create_from_request(request, typ)
    order = models.Order.objects.create_for_cart(cart, session=request.session)
    delivery_formset = forms.DeliveryMethodFormset(data=request.POST or None, queryset=order.groups.all())
    if request.method == 'POST':
        if delivery_formset.is_valid():
            delivery_formset.save(request.session)
            return redirect('satchless-checkout-delivery_details')
    return direct_to_template(request, 'satchless/order/checkout.html',
            {'order': order, 'delivery_formset': delivery_formset})

def delivery_details(request):
    order = models.Order.objects.get_from_session(request.session)
    delivery_forms = forms.get_delivery_details_forms(order, request)
    if len(delivery_forms) == 0:
        return redirect('satchless-checkout-payment_choice')
    if request.method == 'POST':
        are_valid = True
        for form in delivery_forms:
            are_valid = are_valid and form.is_valid()
        if are_valid:
            for form in delivery_forms:
                form.save()
            return redirect('satchless-checkout-payment_choice')
    return direct_to_template(request, 'satchless/order/delivery_details.html',
            {'order': order, 'delivery_forms': delivery_forms})

def payment_choice(request):
    pass
