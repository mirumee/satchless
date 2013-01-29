from django.contrib import messages
import django.forms
import django.forms.models
from django.utils.translation import ugettext
import satchless.cart.app
from satchless.product.forms import registry

from categories.app import product_app

from . import forms
from . import handler
from . import models


class CartApp(satchless.cart.app.MagicCartApp):
    AddToCartHandler = None
    Cart = models.Cart
    CartItem = models.CartItem

cart_app = CartApp(product_app)


class WishlistApp(satchless.cart.app.MagicCartApp):
    app_name = 'wishlist'
    namespace = 'wishlist'
    Cart = models.Wishlist
    CartItem = models.WishlistItem
    CartItemForm = forms.WishlistAddToCartItemForm
    AddToCartHandler = handler.AddToCartOrWishlistHandler

    def __init__(self, cart_app, *args, **kwargs):
        self.cart_app = cart_app
        super(WishlistApp, self).__init__(*args, **kwargs)

    def _get_cart_item_form(self, request, item):
        prefix = 'wishlist-%i' % (item.id,)

        cart = self.cart_app.get_cart_for_request(request)
        variant = item.variant.get_subtype_instance()
        variant_formclass = registry.get_handler(type(variant.product))

        class AddVariantToCartForm(self.CartItemForm, variant_formclass):
            pass

        initial = django.forms.models.model_to_dict(
            item.variant, variant_formclass.base_fields.keys())
        form = AddVariantToCartForm(cart=cart, data=request.POST or None,
                                    product=variant.product, initial=initial,
                                    prefix=prefix)
        return form

    def cart_item_form_valid(self, request, form, item):
        messages.success(request, ugettext('Item added to cart'))
        return super(WishlistApp, self).cart_item_form_valid(request, form, item)

wishlist_app = WishlistApp(cart_app=cart_app, product_app=product_app)
