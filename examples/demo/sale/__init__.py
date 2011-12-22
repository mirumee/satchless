from satchless.pricing import Price, PriceRange, PricingHandler

class SalePricingHandler(PricingHandler):
    def _discount_product(self, product, price):
        if not product.discount:
            return price

        if not isinstance(price, (Price, PriceRange)):
            raise TypeError("Price must be a Price or PriceRange instance")
        return product.discount.get_discount_amount(price)

    def get_variant_price(self, variant, price, **context):
        if context.get('discount', True):
            return self._discount_product(variant.product, price)
        return price

    def get_product_price_range(self, product, price_range, currency, **context):
        if context.get('discount', True):
            return self._discount_product(product, price_range)
        return price_range
