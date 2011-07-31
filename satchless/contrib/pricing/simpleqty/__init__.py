from django.db.models import Sum, Min, Max

from ....pricing import Price, PriceRange, PricingHandler
from . import models

class SimpleQtyPricingHandler(PricingHandler):
    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        try:
            base_price = models.ProductPrice.objects.get(product=variant.product)
        except models.ProductPrice.DoesNotExist:
            return kwargs.pop('price', None)
        cart = kwargs.get('cart', None)
        if base_price.qty_mode == 'product' and cart:
            all_variants = variant.product.variants.all()
            cart_quantity = (cart.items.filter(variant__in=all_variants)
                                       .aggregate(Sum('quantity'))['quantity__sum'] or 0)
            if 'cartitem' in kwargs:
                quantity = cart_quantity
            else:
                quantity += cart_quantity
        price_overrides = (base_price.qty_overrides.filter(min_qty__lte=quantity)
                                                   .order_by('-min_qty'))
        try:
            price = price_overrides[0].price
        except IndexError:
            price = base_price.price
        try:
            offset = variant.variantpriceoffset.price_offset
        except models.VariantPriceOffset.DoesNotExist:
            offset = 0
        price = price + offset
        return Price(net=price, gross=price, currency=currency)

    def get_product_price_range(self, product, currency, **kwargs):
        try:
            base_price = models.ProductPrice.objects.get(product=product)
        except models.ProductPrice.DoesNotExist:
            return kwargs.pop('price', (None, None))
        price_overrides = (base_price.qty_overrides.filter(min_qty__lte=1)
                                                   .order_by('-min_qty'))
        try:
            price = price_overrides[0].price
        except IndexError:
            price = base_price.price
        max_price = min_price = price
        min_offset = base_price.offsets.aggregate(Min('price_offset'))['price_offset__min']
        max_offset = base_price.offsets.aggregate(Max('price_offset'))['price_offset__max']
        if max_offset is not None:
            max_price = max(price, price + max_offset)
        if min_offset is not None:
            min_price = min(price, price + min_offset)
        min_price = Price(net=min_price, gross=min_price, currency=currency)
        max_price = Price(net=max_price, gross=max_price, currency=currency)
        return PriceRange(min_price=min_price, max_price=max_price)
