# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from ..core.app import SatchlessApp
from ..util import JSONResponse
from . import models
from . import forms


class CartApp(SatchlessApp):
    app_name = 'cart'
    namespace = 'cart'
    cart_type = 'cart'
    cart_item_form_class = forms.EditCartItemForm
    cart_item_model = models.CartItem
    cart_model = models.Cart

    cart_templates = [
        'satchless/cart/%(cart_type)s/view.html',
        'satchless/cart/view.html'
    ]

    def get_cart_for_request(self, request):
        return self.cart_model.objects.get_or_create_from_request(request,
                                                                  self.cart_type)

    def _handle_cart(self, cart, request):
        cart_item_forms = []
        for item in cart.items.all():
            prefix = '%s-%i' % (self.cart_type, item.id)
            form = self.cart_item_form_class(data=request.POST or None,
                                             instance=item,
                                             prefix=prefix)
            if request.method == 'POST' and form.is_valid():
                item = form.save()
                self.on_item_updated(item)
                # redirect to ourselves
                return redirect(request.get_full_path())
            cart_item_forms.append(form)
        return {
            'cart': cart,
            'cart_item_forms': cart_item_forms,
        }

    def cart(self, request):
        cart = self.get_cart_for_request(request)
        context = self._handle_cart(cart, request)
        if isinstance(context, HttpResponse):
            return context
        format_data = {
            'cart_type': self.cart_type,
        }
        templates = [t % format_data for t in self.cart_templates]
        response = TemplateResponse(request, templates, context)
        if request.is_ajax():
            return JSONResponse({'total': cart.items.count(),
                                 'html': response.rendered_content})
        return response

    @method_decorator(require_POST)
    def remove_item(self, request, item_pk):
        cart = self.get_cart_for_request(request)
        item = get_object_or_404(cart.items, pk=item_pk)
        cart.set_quantity(item.variant, 0)
        return self.redirect('details')

    def get_urls(self):
        return patterns('',
            url(r'^view/$', self.cart, name='details'),
            url(r'^remove/(?P<item_pk>[0-9]+)/$', self.remove_item,
                name='remove-item'),
        )

cart_app = CartApp()
