# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
import django.db
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from . import forms
from . import handler
from . import models
from ..core.app import SatchlessApp
from ..util import JSONResponse


class CartApp(SatchlessApp):

    app_name = 'cart'
    namespace = 'cart'
    cart_type = 'cart'
    CartItemForm = None
    Cart = None

    cart_templates = [
        'satchless/cart/%(cart_type)s/view.html',
        'satchless/cart/view.html'
    ]

    def __init__(self, *args, **kwargs):
        super(CartApp, self).__init__(*args, **kwargs)
        assert self.Cart, ('You need to subclass CartApp and provide Cart')
        assert self.CartItemForm, ('You need to subclass CartApp and'
                                   ' provide CartItemForm')

    def get_cart_for_request(self, request):
        return self.Cart.objects.get_or_create_from_request(
            request, self.cart_type)

    def _handle_cart(self, cart, request):
        cart_item_forms = []
        for item in cart.get_all_items():
            prefix = '%s-%i' % (self.cart_type, item.id)
            form = self.CartItemForm(data=request.POST or None,
                                     instance=item,
                                     prefix=prefix)
            if request.method == 'POST' and form.is_valid():
                item = form.save()
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
        cart.replace_item(item.variant, 0)
        return self.redirect('details')

    def get_urls(self):
        return patterns('',
            url(r'^view/$', self.cart, name='details'),
            url(r'^remove/(?P<item_pk>[0-9]+)/$', self.remove_item,
                name='remove-item'),
        )

class MagicCartApp(CartApp):
    CartItem = None
    product_app = None

    def __init__(self, product_app, **kwargs):
        self.product_app= product_app
        self.Cart = self.Cart or self.construct_cart_class()
        self.CartItem = (self.CartItem or
                         self.construct_cart_item_class(self.Cart,
                                                        product_app.Variant))
        self.CartItemForm = (
            self.CartItemForm or
            self.construct_cart_item_form_class(self.CartItem))
        self.add_to_cart_handler = handler.AddToCartHandler(
            self.cart_type,
            addtocart_formclass=forms.AddToCartForm,
            cart_class=self.Cart)
        product_app.register_product_view_handler(self.add_to_cart_handler)
        super(MagicCartApp, self).__init__(**kwargs)

    def construct_cart_class(self):
        class Cart(models.Cart):
            pass
        return Cart

    def construct_cart_item_class(self, cart_class, variant_class):
        class CartItem(models.CartItem):
            cart = django.db.models.ForeignKey(cart_class,
                                               related_name='items',
                                               editable=False)
            variant = django.db.models.ForeignKey(variant_class,
                                                  related_name='+',
                                                  editable=False)
        return CartItem

    def construct_cart_item_form_class(self, cart_item_class):
        class EditCartItemForm(forms.EditCartItemForm):
            class Meta:
                model = cart_item_class
        return EditCartItemForm