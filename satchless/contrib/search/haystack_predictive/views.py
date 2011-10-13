# -*- coding:utf-8 -*-
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.template.response import TemplateResponse
from haystack.query import RelatedSearchQuerySet

from ....product.models import Product
from . import forms

PRODUCTS_PER_PAGE = 5

def search_products(request, template_name='satchless/search/haystack_predictive/products.html'):
    form = forms.ProductPredictiveSearchForm(data=request.GET or None)
    if form.is_valid():
        results = form.search()
        query = form.cleaned_data['q']
    else:
        results = RelatedSearchQuerySet().all()
        results = results.load_all()
        results = results.models(Product)
        query = ''
    products_per_page = getattr(settings, 'HAYSTACK_PREDICTIVE_PRODUCTS_PER_PAGE', PRODUCTS_PER_PAGE)
    paginator = Paginator(results, products_per_page)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except InvalidPage:
        raise Http404()
    return TemplateResponse(request, template_name, {
        'form': form,
        'page': page,
        'paginator': paginator,
        'query': query,
    })
