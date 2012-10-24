from satchless.core.handler import QueueHandler

from . import PricingHandler


class PricingQueue(PricingHandler, QueueHandler):
    def get_variant_price(self, variant, currency=None, price=None, quantity=1, **context):
        for handler in self.queue:
            price = handler.get_variant_price(variant=variant,
                                              currency=currency,
                                              quantity=quantity,
                                              price=price,
                                              **context)
        return price

    def get_product_price_range(self, product, currency=None, price_range=None, **context):
        for handler in self.queue:
            price_range = handler.get_product_price_range(product=product,
                                                      currency=currency,
                                                      price_range=price_range,
                                                      **context)
        return price_range
