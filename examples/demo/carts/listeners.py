from django.contrib import messages
from django.utils.translation import ugettext

from satchless.cart import signals

def add_to_cart_listener(sender, instance, request, **kwargs):
    real_variant = instance.variant.get_subtype_instance()
    if instance.cart.typ == 'satchless_cart':
        messages.success(request, ugettext('<strong>Great success!</strong> %s was '
                                    'added to your cart.') % real_variant)
    else:
        messages.success(request, ugettext('<strong>Bookmarked!</strong> %s was added '
                                    'to your wishlist.') % real_variant)

def start_listening():
    signals.cart_item_added.connect(add_to_cart_listener)

