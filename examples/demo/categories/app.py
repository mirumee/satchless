import satchless.category.app

from . import models
import products.models

class CategoryApp(satchless.category.app.CategorizedProductApp):
    Category = models.Category
    Product = products.models.Product
    Variant = products.models.Variant

product_app = CategoryApp()
