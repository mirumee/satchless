from satchless.pricing import Price
from . import models

def _tax_product(product, price):
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

def get_variant_price(variant, quantity=1, **kwargs):
    return _tax_product(variant.product, kwargs.pop('price'))

def get_product_price_range(product, **kwargs):
    return _tax_product(product, kwargs.pop('price_range'))

