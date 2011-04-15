from django.db.models import Min, Max
from ...pricing import Price

class FieldGetter(object):
    def __init__(self, field_name='price', currency=None):
        self.currency = currency
        self.field_name = field_name


class ProductFieldGetter(FieldGetter):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        price = kwargs.pop('price')
        if self.currency and self.currency != currency:
            return price
        try:
            instance_price = getattr(variant.product, self.field_name)
        except AttributeError:
            return price
        return Price(instance_price, instance_price)

    def get_product_price_range(self, product, currency, **kwargs):
        price = kwargs.pop('price')
        if self.currency and self.currency != currency:
            return price
        try:
            instance_price = getattr(product, self.field_name)
        except AttributeError:
            return price
        return (Price(instance_price, instance_price),
                Price(instance_price, instance_price))


class VariantFieldGetter(FieldGetter):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        price = kwargs.pop('price')
        if self.currency and self.currency != currency:
            return price
        try:
            instance_price = getattr(variant, self.field_name)
        except AttributeError:
            return price
        return Price(instance_price, instance_price)

    def get_product_price_range(self, product, currency, **kwargs):
        price = kwargs.pop('price')
        if self.currency and self.currency != currency:
            return price
        minmax = product.variants.all().aggregate(
                    min_price=Min(self.field_name),
                    max_price=Max(self.field_name))
        return (Price(minmax['min_price'], minmax['min_price']),
                Price(minmax['max_price'], minmax['max_price']))
