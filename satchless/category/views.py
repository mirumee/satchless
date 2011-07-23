# -*- coding:utf-8 -*-
from django.http import Http404
from django.http import HttpResponseNotFound

from scbv.views import View

from ..product import views
from . import models

class CategoryIndex(View):
    template_name = 'satchless/category/index.html'

    def get_context_data(self, request, **kwargs):
        context = {
            'categories': models.Category.objects.filter(parent__isnull=True)
        }
        context.update(kwargs)
        return context


class CategoryDetails(View):
    def __call__(self, request, parent_slugs, category_slug):
        slugs = filter(None, parent_slugs.split('/') + [category_slug])
        try:
            path = models.Category.path_from_slugs(slugs)
        except models.Category.DoesNotExist:
            return HttpResponseNotFound()
        category = path[-1]
        return self.respond(self.get_context_data(request, category=category, path=path))


class ProductDetails(views.ProductDetails):
    def get_product(self, request, category_slugs='', product_slug='', product_pk=None):
        path = models.Category.path_from_slugs(filter(None, category_slugs.split('/')))
        products = models.Product.objects.filter(slug=product_slug)
        if product_pk:
            products = products.filter(pk=product_pk)
        if len(path):
            products = products.filter(categories=path[-1])
        elif not request.user.is_staff:
            products = products.filter(categories__isnull=False)
        if not products.exists():
            raise Http404()
        product = products[0].get_subtype_instance()
        product.category_path = path
        return product

    def get_context_data(self, request, product, **kwargs):
        context = {
            'path': product.category_path,
            'product': product,
        }
        context.update(kwargs)
        return context
