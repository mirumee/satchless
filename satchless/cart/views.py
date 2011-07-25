# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from ..util import JSONResponse
from . import models
from . import forms
from . import signals

def cart(request, typ, form_class=forms.EditCartItemForm, extra_context=None):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)

    cart_item_forms = []
    for item in cart.items.all():
        form = form_class(data=request.POST or None, instance=item,
                          prefix='%s-%i'%(typ, item.id))
        if request.method == 'POST' and form.is_valid():
            messages.success(request,
                             _("Cart contents were updated successfully."))
            form.save()
            return redirect(request.get_full_path())
        cart_item_forms.append(form)
    templates = [
        'satchless/cart/%s/view.html' % typ,
        'satchless/cart/view.html'
    ]
    context = {
        'cart': cart,
        'cart_item_forms': cart_item_forms,
    }
    if extra_context:
        context.update(extra_context)
    if request.is_ajax():
        templates = [
            'satchless/cart/%s/ajax_view.html' % typ,
            'satchless/cart/ajax_view.html'
        ]
        response = TemplateResponse(request, templates, context)
        return JSONResponse({'total': cart.items.count(),
                             'html': response.rendered_content})
    return TemplateResponse(request, templates, context)

@require_POST
def remove_item(request, typ, item_pk):
    cart = models.Cart.objects.get_or_create_from_request(request, typ)
    item = get_object_or_404(cart.items, pk=item_pk)
    cart.set_quantity(item.variant, 0)
    signals.cart_item_removed.send(sender=type(item),
                                   instance=item,
                                   request=request)
    return redirect('satchless-cart-view', typ=typ)
