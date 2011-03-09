from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .handler import AddToCartHandler

add_to_cart_handler = AddToCartHandler('satchless_cart')

if not getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None):
    raise ImproperlyConfigured('You need to configure '
                               'SATCHLESS_DEFAULT_CURRENCY')
