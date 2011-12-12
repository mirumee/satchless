from satchless.contrib.pricing.simpleqty import SimpleQtyPricingHandler

from . import models

class DemoPricingHandler(SimpleQtyPricingHandler):
    ProductPrice = models.ProductPrice
    VariantPriceOffset = models.VariantPriceOffset
