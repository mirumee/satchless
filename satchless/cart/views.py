from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from . import models
from . import forms

def cart(request, typ, formset_class=forms.CartItemFormSet):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)
    if request.method == 'POST':
        formset = formset_class(instance=cart, data=request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('satchless-cart-view', kwargs={'typ': typ}))
    else:
        formset = formset_class(instance=cart)
    return render_to_response(
            ['satchless/cart/%s/view.html' % typ, 'satchless/cart/view.html'],
            {'cart': cart, 'formset': formset},
            context_instance=RequestContext(request))
