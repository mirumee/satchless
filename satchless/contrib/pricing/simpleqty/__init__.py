from django.db.models import Min, Max

from ....pricing import Price, PriceRange, PricingHandler

class SimpleQtyPricingHandler(PricingHandler):
    def _get_variants_count(self, variant, currency, quantity, **kwargs):
        cart = kwargs.get('cart', None)
        if cart:
            all_variants = variant.product.variants.all()
            cart_quantity = sum(ci.quantity for ci in cart.get_all_items() if ci.variant in all_variants)
            if 'cartitem' in kwargs:
                quantity = cart_quantity
            else:
                quantity += cart_quantity
        return quantity

    def get_variant_price(self, variant, currency, quantity=1, **kwargs):
        if variant.product.qty_mode == 'product':
            quantity = self._get_variants_count(variant, currency, quantity, **kwargs)
        price_overrides = (variant.product.get_qty_price_overrides().filter(min_qty__lte=quantity)
                                                                    .order_by('-min_qty'))
        try:
            price = price_overrides[0].price
        except IndexError:
            price = variant.product.price
        if variant.price_offset:
            price = price + variant.price_offset
        return Price(net=price, gross=price, currency=currency)

    def get_product_price_range(self, product, currency, **kwargs):
        price_overrides = (product.get_qty_price_overrides().filter(min_qty__lte=1)
                                                            .order_by('-min_qty'))
        try:
            price = price_overrides[0].price
        except IndexError:
            price = product.price
        max_price = min_price = price
        min_offset = product.variants.all().aggregate(Min('price_offset'))['price_offset__min']
        max_offset = product.variants.all().aggregate(Max('price_offset'))['price_offset__max']
        if max_offset is not None:
            max_price = max(price, price + max_offset)
        if min_offset is not None:
            min_price = min(price, price + min_offset)
        min_price = Price(net=min_price, gross=min_price, currency=currency)
        max_price = Price(net=max_price, gross=max_price, currency=currency)
        return PriceRange(min_price=min_price, max_price=max_price)
