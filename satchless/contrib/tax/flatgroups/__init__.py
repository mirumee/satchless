from decimal import Decimal
from satchless.pricing import Price, PriceRange, LinearTax, PricingHandler

from . import models

class FlatGroupPricingHandler(PricingHandler):
    def _tax_product(self, product, price):
        try:
            group = product.taxgroup_set.get()
        except models.TaxGroup.DoesNotExist:
            try:
                group = models.TaxGroup.objects.get(default=True)
            except models.TaxGroup.DoesNotExist:
                return price
        if not isinstance(price, (Price, PriceRange)):
            raise TypeError("Price must be a Price instance or tuple.")
        multiplier = (group.rate + Decimal('100')) / Decimal('100')
        tax = LinearTax(multiplier=multiplier, name=group.name)
        return price + tax

    def get_variant_price(self, variant, price, quantity=1, **kwargs):
        return self._tax_product(variant.product, price)

    def get_product_price_range(self, product, price_range, **kwargs):
        return self._tax_product(product, price_range)
