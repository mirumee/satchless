from satchless.pricing import Price, PricingHandler

from . import models

class SalePricingHandler(PricingHandler):
    def _discount_product(self, product, price):
        try:
            group = product.discount.get()
        except models.DiscountGroup.DoesNotExist:
            return price
        if isinstance(price, Price):
            return group.get_discount_amount(price)
        elif isinstance(price, tuple):
            return (group.get_discount_amount(price[0]), group.get_discount_amount(price[1]))
        raise TypeError("Price must be a Price instance or tuple.")

    def get_variant_price(self, variant, currency, **context):
        if context.get('discount', True):
            return self._discount_product(variant.product, context.pop('price'))
        return context.pop('price')

    def get_product_price_range(self, product, currency, **context):
        if context.get('discount', True):
            return self._discount_product(product, context.pop('price_range'))
        return context.pop('price_range')

