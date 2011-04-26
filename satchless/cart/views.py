from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from . import models
from . import forms

def cart(request, typ, form_class=forms.EditCartItemForm):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)

    cart_item_forms = []
    for item in cart.items.all():
        form = form_class(data=request.POST or None, instance=item,
                          prefix='%s-%i'%(typ, item.id))
        if request.method == 'POST' and form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path)
        cart_item_forms.append(form)

    return render_to_response(
            ['satchless/cart/%s/view.html' % typ, 'satchless/cart/view.html'],
            {'cart': cart, 'cart_item_forms': cart_item_forms},
            context_instance=RequestContext(request))

@require_POST
def remove_item(request, typ, item_pk):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)
    try:
        item = cart.items.get(pk=item_pk)
    except models.CartItem.DoesNotExist:
        raise Http404
    cart.set_quantity(item.variant, 0)
    return HttpResponseRedirect(reverse('satchless-cart-view', kwargs={'typ': typ}))
