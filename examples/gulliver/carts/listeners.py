from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from satchless.cart import signals

def add_to_cart_listener(sender, instance, request, **kwargs):
    real_variant = instance.variant.get_subtype_instance()
    messages.success(request, _('<strong>Great success!</strong>'
                                ' %s was added to the cart.') % real_variant)

signals.cart_item_added.connect(add_to_cart_listener)

