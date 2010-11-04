from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from . import models
from . import forms

def cart(request, typ):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)
    if request.method == 'POST':
        formset = forms.CartItemFormSet(instance=cart, data=request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('satchless-cart-view', kwargs={'typ': typ}))
    else:
        formset = forms.CartItemFormSet(instance=cart)
    return direct_to_template(request,
            'satchless/cart/view.html',
            {'cart': cart, 'formset': formset})
