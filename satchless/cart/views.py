from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_http_methods
from . import models
from . import forms

@require_http_methods(['POST'])
def add_to_cart(request, typ, formclass=forms.AddToCartForm):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)
    form = formclass(cart=cart, data=request.POST)
    if form.is_valid():
        form.save()
    return HttpResponseRedirect(reverse('satchless-cart-view', kwargs={'typ': typ}))

def view_cart(request, typ):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)
    return direct_to_template(request,
            'satchless/cart/view.html',
            {'cart': cart})
