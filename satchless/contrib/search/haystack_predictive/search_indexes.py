import datetime

from django.conf import settings

from haystack import site
from haystack.indexes import *

from satchless.product import models

class ProductEdgeNgramField(EdgeNgramField):
    def __init__(self, fieldname, *args, **kwargs):
        self.fieldname = fieldname
        super(ProductEdgeNgramField, self).__init__(*args, **kwargs)

    def prepare(self, obj):
        product = obj.get_subtype_instance()
        translations = [ getattr(product, self.fieldname) ]
        for product_translation in product.translations.all():
            translations.append(getattr(product_translation, self.fieldname))
        return ' '.join(translations)

class ProductPredictiveSearchIndex(SearchIndex):
    text = ProductEdgeNgramField(fieldname='name', document=True)

    def get_queryset(self):
        return models.Product.objects.all()

site.register(models.Product, ProductPredictiveSearchIndex)
