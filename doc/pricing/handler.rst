.. _pricing-handler:

======================================
Writing you own pricing or tax handler
======================================

Let's assume you want to write a simple pricing handler that applies 5% tax
to the final product price. It will also keep the existing taxes, operating
on the gross price received, no matter how it's related to the net price.

One Python file will suffice. Let's call it ``mytax.py`` and place it a
directory included in ``PYTHONPATH``::

    import decimal
    from satchless.pricing import Price, PricingHandler

    class MyTaxHandler(PricingHandler):
        def get_variant_price(self, variant, **kwargs):
            price = kwargs.pop('price')
            return Price(price.net, price.gross * decimal.Decimal('1.05'))

        def get_product_price_range(self, product, **kwargs):
            hi, lo = kwargs.pop('price_range')
            return (Price(lo.net, lo.gross * decimal.Decimal('1.05')),
                    Price(hi.net, hi.gross * decimal.Decimal('1.05')))

After that, append your new handler to the end of the chain in ``settings.py``::

    SATCHLESS_PRICING_HANDLERS = [
        'satchless.contrib.pricing.simpleqty.SimpleQtyPricingHandler',
        ...
        'mytax.MyTaxHandler',
    ]
