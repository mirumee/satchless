from django.contrib import messages
from django.utils.translation import ugettext

from satchless.cart import signals

def add_to_cart_listener(sender, instance, request, result, **kwargs):
    real_variant = instance.variant.get_subtype_instance()
    if result.quantity_delta > 0:
        if instance.cart.typ == 'satchless_cart':
            messages.success(request, ugettext(u'<strong>Great success!</strong> %s was '
                                                'added to your cart.') % real_variant)
        else:
            messages.success(request, ugettext(u'<strong>Bookmarked!</strong> %s was added '
                                                'to your wishlist.') % real_variant)

def start_listening():
    signals.cart_item_added.connect(add_to_cart_listener)

