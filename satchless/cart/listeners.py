from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from satchless.product.signals import product_view

from . import models
from . import forms

def _to_cart(sender, instance=None, request=None, response=None,
        extra_context=None, typ='', **kwargs):
    """
    Finds AddToCartForm subclass for model and adds it to the context.
    If the request has been POSTed, it also inits the form with the data
    and tries to validate it.
    """
    Form = forms.addtocart_factory(instance.get_variant_formclass())
    form = Form(data=request.POST or None, product=instance, typ=typ)
    if request.method == 'POST':
        if form.is_valid() and len(response) == 0:
            cart = models.Cart.objects.get_or_create_from_request(request, typ)
            form.save(cart=cart)
            response.append(HttpResponseRedirect(reverse('satchless-cart-view', kwargs={'typ': typ})))
    extra_context['%s_form' % typ] = form

def addtocart_listener(typ):
    def do_listener(*args, **kwargs):
        return _to_cart(typ=typ, *args, **kwargs)
    return do_listener

def qpa(*args, **kwargs):
    _to_cart(typ='satchless_cart', *args, **kwargs)

product_view.connect(addtocart_listener('satchless_cart'))
product_view.connect(qpa)
