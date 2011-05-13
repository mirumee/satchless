# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from satchless.product.models import Category, Product

from . import models
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

    ProductCategory = Product.categories.through
    discounted_products = ProductCategory.objects.filter(product__discount__isnull=False) \
                                                        .values_list('category_id', flat=True)
    categories = query.add_filtered_related_count(Category.tree, Category.tree.root_nodes(),
                                                  discounted_products, 'category', 'products_count',
                                                  cumulative=True)
    categories = filter(lambda cat: cat.products_count, categories)
    return direct_to_template(request, "sale/index.html", {
        'category': category,
        'categories': categories,
        'path': path,
        'products': products,
    })


