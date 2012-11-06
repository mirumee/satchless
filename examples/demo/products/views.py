# -*- coding:utf-8 -*-
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse

from categories.app import product_app

from . import query


def sales(request, category_slugs=None):
    if category_slugs:
        category_slugs = filter(None, category_slugs.split('/'))
        try:
            path = product_app.path_from_slugs(category_slugs)
        except product_app.Category.DoesNotExist:
            return HttpResponseNotFound()
        category = path[-1]
        products = product_app.Product.objects.filter(categories__lft__gte=category.lft,
                                                      categories__rght__lte=category.rght,
                                                      categories__tree_id=category.tree_id,
                                                      discount__isnull=False)
    else:
        category = None
        products = product_app.Product.objects.filter(discount__isnull=False)
        path = []
    ProductCategory = product_app.Product.categories.through
    discounted_products = (ProductCategory.objects.filter(product__discount__isnull=False)
                                                  .values_list('category_id',
                                                               flat=True))
    categories = query.add_filtered_related_count(product_app.Category.tree,
                                                  product_app.Category.tree.root_nodes(),
                                                  discounted_products,
                                                  'category',
                                                  'products_count',
                                                  cumulative=True)
    categories = filter(lambda c: c.products_count, categories)
    return TemplateResponse(request, 'sale/index.html', {
        'categories': categories,
        'category': category,
        'path': path,
        'products': products,
    })
