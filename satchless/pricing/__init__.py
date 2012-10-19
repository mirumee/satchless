class PricingHandler(object):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        raise NotImplementedError()

    def get_product_price_range(self, product, currency, **kwargs):
        raise NotImplementedError()


class StopPropagation(Exception):
    pass
