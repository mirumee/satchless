from django.shortcuts import redirect

from ..product.models import Product, Variant
from ..util import JSONResponse
from . import forms
from . import signals


class AddToCartHandler(object):
    """
    Parametrized handler for `product_view`, which produces *add to cart* forms,
    validates them and performs all the logic of adding an item to a cart.
    """

    def __init__(self, cart_app, addtocart_formclass=forms.AddToCartForm,
                 form_attribute='cart_form'):
        """
        Sets up a parametrized handler for product view.

        Accepts:

            * `details_view`: the cart view to redirect to
            * `addtocart_formclass`: form class responsible for adding to cart.
            * `form_attribute`: name of instance's attribute to save the form under.
        """
        self.cart_app = cart_app
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

            Form = forms.add_to_cart_variant_form_for_product(product,
                    addtocart_formclass=self.addtocart_formclass)
            cart = self.cart_app.get_cart_for_request(request)
            if request.method == 'POST':
                form = Form(cart=cart, data=request.POST, product=product,
                            variant=variant)
                if form.is_valid():
                    form_result = form.save()
                    signals.cart_item_added.send(sender=type(form_result.cart_item),
                                                 instance=form_result.cart_item,
                                                 result=form_result,
                                                 request=request)
                    if request.is_ajax():
                        # FIXME: add cart details like number of items and new total
                        return JSONResponse({})
                    return redirect(self.cart_app.reverse('details'))
                elif request.is_ajax() and form.errors:
                    data = dict(form.errors)
                    return JSONResponse(data, status=400)
            else:
                form = Form(cart=cart, data=None, product=product,
                            variant=variant)
            # Attach the form to instance
            setattr(instance, self.form_attribute, form)
        return extra_context
