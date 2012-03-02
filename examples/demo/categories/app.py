import satchless.category.app
from satchless.pricing.app import ProductAppPricingMixin

from . import models
import products.models

class CategorizedProductApp(ProductAppPricingMixin,
                            satchless.category.app.CategorizedProductApp):
    Category = models.Category
    Product = products.models.Product
    Variant = products.models.Variant

product_app = CategorizedProductApp()
