from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.simple import direct_to_template
from . import models

def index(request, *args, **kwargs):
    return HttpResponse("<p>%s</p><p>%s</p>" % (args, kwargs))

def category(request, parent_slugs, category_slug):
    try:
        path = models.Category.path_from_slugs(filter(None, parent_slugs.split('/') + [category_slug]))
    except models.Category.DoesNotExist:
        return HttpResponseNotFound()
    category = path[-1]
    return direct_to_template(request,
            'satchless/product/category.html',
            {'category': category, 'path': path})

def product(request, category_slugs='', product_slug=''):
    path = models.Category.path_from_slugs(filter(None, category_slugs.split('/')))
    products = models.Product.objects.filter(slug=product_slug)
    if len(path):
        products = products.filter(categories=path[-1])
    if products.count() == 0:
        return HttpResponseNotFound()
    product = products[0]
    return direct_to_template(request,
            'satchless/product/product.html',
            {'product': product, 'path': path})
