from django.views.generic.simple import direct_to_template
from satchless.cart.models import Cart

from . import models
from . import forms

def checkout(request, typ):
    cart = Cart.objects.get_or_create_from_request(request, typ)
    order = models.Order.objects.create_for_cart(cart)
    print order.groups.all()
    delivery_formset = forms.DeliveryMethodFormset(queryset=order.groups.all())
    return direct_to_template(request, 'satchless/order/checkout.html',
            {'order': order, 'delivery_formset': delivery_formset})
