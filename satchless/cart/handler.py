from django.shortcuts import redirect

from ..product.forms import NonConfigurableVariantForm
from ..product.models import ProductAbstract, Variant
from ..product.signals import product_view, variant_formclass_for_product
from . import forms
from . import models

class AddToCartHandler(object):
    """
    Parametrized handler for `product_view`, which produces *add to cart* forms,
    validates them and performs all the logic of adding an item to a cart.
    """

    def __init__(self, typ='satchless_cart', addtocart_formclass=forms.AddToCartForm,
                 form_attribute='cart_form'):
        """
        Sets up a parametrized handler for product view.

        Accepts:

            * `typ`: the type of the cart to add to
            * `addtocart_formclass`: form class responsible for adding to cart.
            * `form_attribute`: name of instance's attribute to save the form under.
        """
        self.typ = typ
        self.form_attribute = form_attribute
        self.addtocart_formclass = addtocart_formclass

    def build_formclass(self, variant_formclass):
        class AddVariantToCartForm(self.addtocart_formclass, variant_formclass):
            pass
        return AddVariantToCartForm

    def __call__(self, instances=None, request=None, extra_context=None, **kwargs):
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
            formclass = []
            if isinstance(instance, ProductAbstract):
                product = instance
                variant = None
            elif isinstance(instance, Variant):
                product = instance.product
                variant = instance
            else:
                raise ValueError("Received unknown type: %s" %
                                 type(instance).__name__)
            variant_formclass_for_product.send(sender=type(product),
                                               instance=product,
                                               formclass=formclass)
            if len(formclass) > 1:
                raise ValueError("Multiple form classes returned for %s : %s." %
                                 (product._meta.object_name, formclass))
            elif not len(formclass):
                formclass = [NonConfigurableVariantForm]
            Form = self.build_formclass(formclass[0])
            if request.method == 'POST':
                cart = models.Cart.objects.get_or_create_from_request(request,
                                                                      self.typ)
                form = Form(data=request.POST, cart=cart, product=product,
                            variant=variant, typ=self.typ)
                if form.is_valid():
                    form.save()
                    return redirect('satchless-cart-view', typ=self.typ)
            else:
                form = Form(data=None, product=product, variant=variant,
                            typ=self.typ)
            # Attach the form to instance
            setattr(instance, self.form_attribute, form)
        return extra_context

