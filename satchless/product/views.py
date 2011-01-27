from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.simple import direct_to_template
from django.shortcuts import render_to_response
from django.template import RequestContext
from . import models
from . import signals

def index(request, *args, **kwargs):
    """Show root categories"""
    categories = models.Category.objects.filter(parent__isnull=True)
    return direct_to_template(request, 'satchless/product/index.html',
                              {'categories': categories})

def category(request, parent_slugs, category_slug):
    slugs = filter(None, parent_slugs.split('/') + [category_slug])
    try:
        path = models.Category.path_from_slugs(slugs)
    except models.Category.DoesNotExist:
        return HttpResponseNotFound()
    category = path[-1]
    return direct_to_template(request, 'satchless/product/category.html',
                              {'category': category, 'path': path})

def product(request, category_slugs='', product_slug='', product_pk=None):
    path = models.Category.path_from_slugs(filter(None, category_slugs.split('/')))
    products = models.Product.objects.filter(slug=product_slug)
    if product_pk:
        products = products.filter(pk=product_pk)
    if len(path):
        products = products.filter(categories=path[-1])
    if not products.exists():
        return HttpResponseNotFound()
    product = products[0].get_subtype_instance()
    context = {}
    response = []
    signals.product_view.send(sender=type(product), instances=[product],
                              request=request, response=response,
                              extra_context=context)
    if len(response) == 1:
        return response[0]
    elif len(response) > 1:
        raise ValueError, "Multiple responses returned."
    context['product'] = product
    context['path'] = path
    templates = [
        'satchless/product/%s_%s_view.html' %
        (product._meta.module_name, product._meta.object_name.lower()),
        'satchless/product/%s_view.html' % product._meta.module_name,
        'satchless/product/view.html',
    ]
    return render_to_response(templates, context,
                              context_instance=RequestContext(request))
