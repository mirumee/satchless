from django.db.models import Min, Max
from prices import Price, PriceRange

from ....pricing import PricingHandler


class FieldGetter(object):
    def __init__(self, field_name='price', currency=None):
        self.currency = currency
        self.field_name = field_name


class ProductFieldGetter(FieldGetter, PricingHandler):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        price = kwargs.pop('price')
        if self.currency and self.currency != currency:
            return price
        cur = currency.lower() if currency else ''
        field_name = self.field_name % {'currency': cur}
        try:
            instance_price = getattr(variant.product, field_name)
        except AttributeError:
            return price
        return Price(instance_price, instance_price, currency=currency)

    def get_product_price_range(self, product, currency, **kwargs):
        price_range = kwargs.pop('price_range')
        if self.currency and self.currency != currency:
            return price_range
        cur = currency.lower() if currency else ''
        field_name = self.field_name % {'currency': cur}
        try:
            instance_price = getattr(product, field_name)
        except AttributeError:
            return price_range
        min_price = Price(instance_price, instance_price, currency=currency)
        max_price = Price(instance_price, instance_price, currency=currency)
        return PriceRange(min_price=min_price, max_price=max_price)


class VariantFieldGetter(FieldGetter, PricingHandler):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        price = kwargs.pop('price')
        if self.currency and self.currency != currency:
            return price
        cur = currency.lower() if currency else ''
        field_name = self.field_name % {'currency': cur}
        try:
            instance_price = getattr(variant, field_name)
        except AttributeError:
            return price
        return Price(instance_price, instance_price, currency=currency)

    def get_product_price_range(self, product, currency, **kwargs):
        price_range = kwargs.pop('price_range')
        if self.currency and self.currency != currency:
            return price_range
        cur = currency.lower() if currency else ''
        field_name = self.field_name % {'currency': cur}
        minmax = product.variants.all().aggregate(min_price=Min(field_name),
                                                  max_price=Max(field_name))
        min_price = Price(minmax['min_price'], minmax['min_price'],
                          currency=currency)
        max_price = Price(minmax['max_price'], minmax['max_price'],
                          currency=currency)
        return PriceRange(min_price=min_price, max_price=max_price)
