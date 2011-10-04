# -*- coding:utf-8 -*-
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse

from satchless.category.models import Category
from satchless.product.models import Product

from . import query

def index(request, category_slugs=None):
    if category_slugs:
        category_slugs = filter(None, category_slugs.split('/'))
        try:
            path = Category.path_from_slugs(category_slugs)
        except Category.DoesNotExist:
            return HttpResponseNotFound()
        category = path[-1]
        products = Product.objects.filter(categories__lft__gte=category.lft,
                                          categories__rght__lte=category.rght,
                                          categories__tree_id=category.tree_id,
                                          discount__isnull=False)
    else:
        category = None
        products = Product.objects.filter(discount__isnull=False)
        path = []
    ProductCategory = Product.categories.related.field.rel.through
    discounted_products = (ProductCategory.objects.filter(product__discount__isnull=False)
                                                  .values_list('category_id',
                                                               flat=True))
    categories = query.add_filtered_related_count(Category.tree,
                                                  Category.tree.root_nodes(),
                                                  discounted_products,
                                                  'category',
                                                  'products_count',
                                                  cumulative=True)
    categories = filter(lambda cat: cat.products_count, categories)
    return TemplateResponse(request, 'sale/index.html', {
        'categories': categories,
        'category': category,
        'path': path,
        'products': products,
    })
