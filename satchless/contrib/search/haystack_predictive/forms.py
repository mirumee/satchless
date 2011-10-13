# -*- coding:utf-8 -*-
from haystack.forms import SearchForm
from haystack.query import RelatedSearchQuerySet

from ....product.models import Product

class ProductPredictiveSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('searchqueryset', None):
            kwargs['searchqueryset'] = RelatedSearchQuerySet()
        super(ProductPredictiveSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        if self.cleaned_data.get('q', None):
            sqs = self.searchqueryset.autocomplete(text=self.cleaned_data['q'])
        else:
            sqs = self.searchqueryset.all()
        if self.load_all:
            sqs = sqs.load_all()
        return sqs.models(Product)

