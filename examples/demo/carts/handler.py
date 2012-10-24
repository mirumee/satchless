from django.shortcuts import redirect
from satchless.cart import signals
from satchless.django.product.models import Product, Variant
from satchless.util import JSONResponse
import satchless.cart.forms

from . import forms


class AddToCartOrWishlistHandler(object):
    def __init__(self, cart_app, addtocart_formclass=forms.AddToCartForm,
                 form_attribute='cart_form'):
        self.wishlist_app = cart_app
        self.form_attribute = form_attribute
        self.addtocart_formclass = addtocart_formclass

    def __call__(self, instances=None, request=None, extra_context=None,
                 **kwargs):
        """
        Accepts a list of Product or Variant instances. For every of them finds
        add-to-cart form. For a POST request, performs validation and if it
        succeeds, adds item to cart and returns redirect to the cart page.

        It handles adding only a single variant to the cart, but with the quantity
        specified in request.

        Accepts parameters:

            * `instances`: products and/or variants being viewed
            * `request`: the HTTP request instance
            * `extra_context`: extra context that will be passed to template
        """
        for instance in instances:
            if isinstance(instance, Product):
                product = instance
                variant = None
            elif isinstance(instance, Variant):
                product = instance.product
                variant = instance
            else:
                raise ValueError("Received unknown type: %s" %
                                 type(instance).__name__)

            Form = satchless.cart.forms.add_to_cart_variant_form_for_product(product,
                    addtocart_formclass=self.addtocart_formclass)
            wishlist = self.wishlist_app.get_cart_for_request(request)
            cart = self.wishlist_app.cart_app.get_cart_for_request(request)
            if request.method == 'POST':
                form = Form(data=request.POST, cart=cart, wishlist=wishlist,
                            product=product, variant=variant)
                if form.is_valid():
                    form_result = form.save()
                    signals.cart_item_added.send(sender=type(form_result.cart_item),
                                                 instance=form_result.cart_item,
                                                 result=form_result,
                                                 request=request)
                    if request.is_ajax():
                        # FIXME: add cart details like number of items and new total
                        return JSONResponse({})
                    if form_result.cart_item.cart == wishlist:
                        return redirect(self.wishlist_app.reverse('details'))
                    else:
                        return redirect(self.wishlist_app.cart_app.reverse('details'))
                elif request.is_ajax() and form.errors:
                    data = dict(form.errors)
                    return JSONResponse(data, status=400)
            else:
                form = Form(cart=cart, wishlist=wishlist,
                            data=None, product=product, variant=variant)
            # Attach the form to instance
            setattr(instance, self.form_attribute, form)
        return extra_context

