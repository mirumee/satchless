import urllib

from ....util.exceptions import FinalValue
from ....pricing import PricingHandler

def get_cache_key(currency, product=None, variant=None, **kwargs):
    ret = {'currency': currency}
    if variant:
        ret['variant'] = variant.id
    if product:
        ret['product'] = product.id
    return ret

class CacheFactory(object):
    class Handler(object):
        def __init__(self, get_key_callback):
            self.get_cache_key = get_key_callback

        def get_key(self, **kwargs):
            return urllib.urlencode(self.get_cache_key(**kwargs), True)

    class SetHandler(Handler, PricingHandler):
        def get_variant_price(self, **kwargs):
            from django.core.cache import cache
            price = kwargs.get('price', None)
            if not price:
                raise ValueError('No price passed to Cache.SetHandler')
            key = 'price:' + self.get_key(**kwargs)
            cache.set(key, price)
            return price

        def get_product_price_range(self, **kwargs):
            from django.core.cache import cache
            price_range = kwargs.get('price_range', None)
            if not price_range:
                raise ValueError('No price_range passed to Cache.SetHandler')
            key = 'pricerange:' + self.get_key(**kwargs)
            cache.set(key, price_range)
            return price_range


    class GetHandler(Handler, PricingHandler):
        def get_variant_price(self, **kwargs):
            from django.core.cache import cache
            key = 'price:' + self.get_key(**kwargs)
            price = cache.get(key)
            if price:
                raise FinalValue(price)
            return kwargs.get('price')

        def get_product_price_range(self, **kwargs):
            from django.core.cache import cache

            key = 'pricerange:' + self.get_key(**kwargs)
            price_range = cache.get(key)
            if price_range:
                raise FinalValue(price_range)
            return kwargs.get('price_range')

    def __init__(self, get_key_callback=get_cache_key):
        self.setter = self.SetHandler(get_key_callback)
        self.getter = self.GetHandler(get_key_callback)
