from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from satchless.product.forms import NonConfigurableVariantForm
from satchless.product.signals import product_view, variant_formclass_for_product
from satchless.product.models import ProductAbstract, Variant

from . import models
from . import forms

def _to_cart(sender, instances=None, request=None, response=None,
        extra_context=None, typ='', **kwargs):
    """
    Accepts a list of Product or Variant instances. For every of them finds
    add-to-cart form. For a POST request, performs validation and if it
    succeeds, adds item to cart and returns redirect to the cart page.

    It handles adding only a single variant to the cart, but with the quantity
    specified in request.
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
            raise ValueError("Received unknown type: %s" % type(instance).__name__)
        variant_formclass_for_product.send(sender=type(product), instance=product, formclass=formclass)
        if len(formclass) > 1:
            raise ValueError("Multiple form classes returned for %s : %s." % (
                product._meta.object_name, formclass))
        elif not len(formclass):
            formclass = [NonConfigurableVariantForm]
        Form = forms.addtocart_factory(formclass[0])
        form = Form(data=request.POST or None, product=product, variant=variant, typ=typ)
        if request.method == 'POST':
            if form.is_valid() and len(response) == 0:
                cart = models.Cart.objects.get_or_create_from_request(request, typ)
                form.save(cart=cart)
                response.append(HttpResponseRedirect(reverse('satchless-cart-view', kwargs={'typ': typ})))
                return
        instance.cart_form = form

def addtocart_listener(typ):
    def do_listener(*args, **kwargs):
        return _to_cart(typ=typ, *args, **kwargs)
    return do_listener

# Bind with strong reference, as the generated function goes off-scope anw would be garbage collected.
product_view.connect(addtocart_listener('satchless_cart'), weak=False)

# Example: add to wishlist:
#product_view.connect(addtocart_listener('satchless_wishlist'), weak=False)
