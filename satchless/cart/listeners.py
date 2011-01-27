from django.shortcuts import redirect
from satchless.product.forms import NonConfigurableVariantForm
from satchless.product.signals import product_view, variant_formclass_for_product
from satchless.product.models import ProductAbstract, Variant

from . import forms
from . import models

class AddToCartListener(object):
    """
    Parametrized listener for `product_view` signal, which produces *add to cart* forms,
    validates them and performs all the logic of adding an item to cart.
    """

    def __init__(self, typ, addtocart_formclass=forms.AddToCartForm,
                 form_attribute='cart_form'):
        """
        Sets up a parametrized listener for `product_view` signal.

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

    def __call__(self, sender, instances=None, request=None, response=None,
                 extra_context=None, **kwargs):
        """
        Accepts a list of Product or Variant instances. For every of them finds
        add-to-cart form. For a POST request, performs validation and if it
        succeeds, adds item to cart and returns redirect to the cart page.

        It handles adding only a single variant to the cart, but with the quantity
        specified in request.

        Accepts parameters:

            * `sender`: sender class
            * `instances`: products and/or variants being viewed
            * `request`: the HTTP request instance
            * `response`: a list of responses to be filled by listeners
            * `extra_context`: extra context that will be passed to template
        """
        if response:
            # Someone else has already handled the data and returned HttpResponse.
            return
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
                if form.is_valid() and len(response) == 0:
                    form.save()
                    response.append(redirect('satchless-cart-view',
                                             typ=self.typ))
                    return
            else:
                form = Form(data=None, product=product, variant=variant,
                            typ=self.typ)
            # Attach the form to instance
            setattr(instance, self.form_attribute, form)

# Bind with strong reference as the generated function falls out-of-scope
# and would be garbage collected otherwise.
product_view.connect(AddToCartListener('satchless_cart'), weak=False)
