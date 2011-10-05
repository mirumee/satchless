import urllib
from satchless.core.handler import QueueHandler
from ....pricing import PricingHandler


class PricingCacheHandler(PricingHandler, QueueHandler):
    def get_cache_key(self, currency=None, product=None, variant=None, **kwargs):
        ret = {'currency': currency}
        if variant:
            ret['variant'] = variant.id
        if product:
            ret['product'] = product.id
        return ret

    def _get_key(self, **kwargs):
        return urllib.urlencode(self.get_cache_key(**kwargs), True)

    def get_variant_price(self, variant, currency, price, quantity=1, **context):
        # Visit cache for a matching entry first
        from django.core.cache import cache
        key = 'price:' + self._get_key(currency=currency,
                                    variant=variant,
                                    **context)
        price = cache.get(key)
        if price:
            return price
        # Iterate queue and caculate the price to be cached
        price = None
        for unique_id, handler in self.queue:
            price = handler.get_variant_price(variant=variant,
                                              currency=currency,
                                              quantity=quantity,
                                              price=price,
                                              **context)
        # Send returned price to the cache
        cache.set(key, price)
        return price

    def get_product_price_range(self, product, currency, price_range, **context):
        # Visit cache for a matching entry first
        from django.core.cache import cache
        key = 'pricerange:' + self._get_key(**context)
        price_range = cache.get(key)
        if price_range:
            return price_range
        # Iterate queue and caculate the price to be cached
        for unique_id, handler in self.queue:
            price_range = handler.get_product_price_range(product=product,
                                                      currency=currency,
                                                      price_range=price_range,
                                                      **context)
        # Send returned price to the cache
        cache.set(key, price_range)
        return price_range
