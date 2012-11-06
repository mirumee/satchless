import satchless.category.app

from . import models
import products.models


class CategorizedProductApp(satchless.category.app.CategorizedProductApp):
    Category = models.Category
    Product = products.models.Product
    Variant = products.models.Variant

product_app = CategorizedProductApp()
