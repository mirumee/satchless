# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ..core.app import SatchlessApp
from ..util import JSONResponse
from . import models
from . import forms

class CartApp(SatchlessApp):
    cart_item_form_class = forms.EditCartItemForm
    cart_model = models.Cart
    cart_item_model = models.CartItem
    cart_templates = [
        'satchless/cart/%(cart_type)s/view.html',
        'satchless/cart/view.html'
    ]
    cart_type = 'satchless_cart'
    cart_url = 'satchless-cart-view'

    def get_cart_for_request(self, request):
        cart_type = self.cart_type
        return self.cart_model.objects.get_or_create_from_request(request,
                                                                  cart_type)

    def get_template_names(self, **kwargs):
        template_data = {
            'cart_type': self.cart_type,
        }
        return [t % template_data for t in self.cart_templates]

    def respond(self, request, context, cart, **kwargs):
        response = TemplateResponse(request, self.get_template_names(**kwargs),
                                    context)
        if request.is_ajax():
            return JSONResponse({'total': cart.items.count(),
                                 'html': response.rendered_content})
        return response

    def on_cart_updated(self, item):
        pass

    def cart(self, request):
        cart = self.get_cart_for_request(request)
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
        context = {
            'cart': cart,
            'cart_item_forms': cart_item_forms,
        }
        return self.respond(request, context, cart=cart)

    @require_POST
    def remove_item(self, request, item_pk):
        cart = self.get_cart_for_request(request)
        item = get_object_or_404(cart.items, pk=item_pk)
        cart.set_quantity(item.variant, 0)
        self.on_item_deleted(item)
        return redirect(self.cart_url)

    def get_urls(self, prefix=None):
        prefix = prefix or 'satchless-cart'
        return patterns('',
            url(r'^view/$', self.cart, name='%s-view' % prefix),
            url(r'^remove/(?P<item_pk>[0-9]+)/$', self.remove_item,
                name='%s-remove-item' % prefix),
        )

cart_app = CartApp()
