from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from satchless.core.handler import QueueHandler

from . import PricingHandler


class PricingQueue(PricingHandler, QueueHandler):
    def get_variant_price(self, variant, currency=None, price=None, quantity=1, **context):
        price = price
        for unique_id, handler in self.queue:
            price = handler.get_variant_price(variant=variant,
                                              currency=currency,
                                              quantity=quantity,
                                              price=price,
                                              **context)
        return price

    def get_product_price_range(self, product, currency=None, price_range=None, **context):
        price_range = price_range
        for unique_id, handler in self.queue:
            price_range = handler.get_product_price_range(product=product,
                                                      currency=currency,
                                                      price_range=price_range,
                                                      **context)
        return price_range


if not getattr(settings, 'SATCHLESS_PRICING_HANDLERS', None):
    raise ImproperlyConfigured('You need to configure '
                               'SATCHLESS_PRICING_HANDLERS')
pricing_queue = PricingQueue(*settings.SATCHLESS_PRICING_HANDLERS)
