# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from . import forms
from . import handler
from . import models
from ..core.app import SatchlessApp, view
from ..util import JSONResponse
from ..util.models import construct


class CartApp(SatchlessApp):

    app_name = 'cart'
    namespace = 'cart'
    CartItemForm = None
    Cart = None

    cart_templates = [
        'satchless/cart/view.html'
    ]

    def __init__(self, *args, **kwargs):
        super(CartApp, self).__init__(*args, **kwargs)
        assert self.Cart, ('You need to subclass CartApp and provide Cart')
        assert self.CartItemForm, ('You need to subclass CartApp and'
                                   ' provide CartItemForm')

    def get_cart_for_request(self, request):
        raise NotImplementedError()

    def _get_cart_item_form(self, request, item):
        prefix = 'cart-%i' % (item.id,)
        form = self.CartItemForm(data=request.POST or None,
                                 instance=item,
                                 prefix=prefix)
        return form

    def cart_item_form_valid(self, request, form, item):
        form.save()
        return redirect(request.get_full_path())

    def _handle_cart(self, cart, request):
        cart_item_forms = []
        for item in cart.get_all_items():
            form = self._get_cart_item_form(request, item)
            if request.method == 'POST' and form.is_valid():
                return self.cart_item_form_valid(request, form, item)
            cart_item_forms.append(form)
        return {
            'cart': cart,
            'cart_item_forms': cart_item_forms,
        }

    @view(r'^view/$', name='details')
    def cart(self, request):
        cart = self.get_cart_for_request(request)
        context = self._handle_cart(cart, request)
        if isinstance(context, HttpResponse):
            return context
        context = self.get_context_data(request, **context)
        response = TemplateResponse(request, self.cart_templates, context)
        if request.is_ajax():
            return JSONResponse({'total': len(cart.get_all_items()),
                                 'html': response.rendered_content})
        return response

    @view(r'^remove/(?P<item_pk>[0-9]+)/$', name='remove-item')
    @method_decorator(require_POST)
    def remove_item(self, request, item_pk):
        cart = self.get_cart_for_request(request)
        try:
            item = cart.get_item(pk=item_pk)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
        cart.replace_item(item.variant, 0)
        return self.redirect('details')


class MagicCartApp(CartApp):

    CartItem = None
    AddToCartHandler = handler.AddToCartHandler

    def __init__(self, product_app, **kwargs):
        self.product_app = product_app

        self.Cart = self.Cart or self.construct_cart_class()
        self.CartItem = (self.CartItem or
                         self.construct_cart_item_class(self.Cart,
                                                        product_app.Variant))
        self.CartItemForm = (
            self.CartItemForm or
            self.construct_cart_item_form_class(self.CartItem))
        if self.AddToCartHandler:
            add_to_cart_handler = self.AddToCartHandler(cart_app=self)
            product_app.register_product_view_handler(add_to_cart_handler)
        super(MagicCartApp, self).__init__(**kwargs)

    def construct_cart_class(self):
        class Cart(models.Cart):
            pass
        return Cart

    def construct_cart_item_class(self, cart_class, variant_class):
        class CartItem(construct(models.CartItem, cart=cart_class,
                                 variant=variant_class)):
            pass
        return CartItem

    def construct_cart_item_form_class(self, cart_item_class):
        class EditCartItemForm(forms.EditCartItemForm):
            class Meta:
                model = cart_item_class

        return EditCartItemForm

    @property
    def cart_session_key(self):
        return '_satchless_cart'

    def get_cart_for_request(self, request):
        try:
            token = request.session[self.cart_session_key]
            cart = self.Cart.objects.get(token=token)
        except (self.Cart.DoesNotExist, KeyError):
            owner = request.user if request.user.is_authenticated() else None
            cart = self.Cart.objects.create(owner=owner)
            request.session[self.cart_session_key] = cart.token
        if cart.owner is None and request.user.is_authenticated():
            cart.owner = request.user
            cart.save()
        return cart
