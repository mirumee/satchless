from django.http import HttpResponseNotFound, HttpResponse
from django.views.generic.simple import direct_to_template
from django.shortcuts import render_to_response
from django.template import RequestContext
from . import models
from . import signals
from . import handler

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
    elif not request.user.is_staff:
        products = products.filter(categories__isnull=False)
    if not products.exists():
        return HttpResponseNotFound()
    product = products[0].get_subtype_instance()
    context = handler.product_view(instances=[product], request=request)
    if isinstance(context, HttpResponse):
        return context

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
