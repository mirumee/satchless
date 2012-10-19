from decimal import Decimal
from prices import Price, PriceRange, LinearTax

from ....pricing import PricingHandler
from . import models


class FlatGroupPricingHandler(PricingHandler):

    TaxGroup = models.TaxGroup

    def _tax_product(self, product, price):
        if not product.tax_group or not price:
            return price
        if not isinstance(price, (Price, PriceRange)):
            raise TypeError("Price must be a Price instance or tuple.")
        multiplier = product.tax_group.rate / Decimal('100')
        tax = LinearTax(multiplier=multiplier, name=product.tax_group.name)
        return price + tax

    def get_variant_price(self, variant, price, quantity=1, **kwargs):
        return self._tax_product(variant.product, price)

    def get_product_price_range(self, product, price_range, **kwargs):
        return self._tax_product(product, price_range)
