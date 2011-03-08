# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from satchless.product.models import Category, Product

from . import models
from . import query

def index(request):
    ProductCategory = Product.categories.through
    categories = query.add_filtered_related_count(Category.tree, Category.tree.root_nodes(),
                                                  ProductCategory.objects.all().values_list('category_id', flat=True),
                                                  'category', 'products_count', cumulative=True)
    categories = filter(lambda cat: cat.products_count, categories)
    return direct_to_template(request, "sale/index.html", {
        'categories': categories,
    })


