from satchless.pricing import Price, PricingHandler
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
        if isinstance(price, Price):
            return group.get_tax_amount(price)
        elif isinstance(price, tuple):
            return (group.get_tax_amount(price[0]), group.get_tax_amount(price[1]))
        raise TypeError("Price must be a Price instance or tuple.")

    def get_variant_price(self, variant, quantity=1, **kwargs):
        return self._tax_product(variant.product, kwargs.pop('price'))

    def get_product_price_range(self, product, **kwargs):
        return self._tax_product(product, kwargs.pop('price_range'))
