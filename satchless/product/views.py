from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.simple import direct_to_template
from . import models
from . import signals

def index(request, *args, **kwargs):
    """Show root categories"""
    categories = models.Category.objects.filter(parent__isnull=True)
    return direct_to_template(request,
            'satchless/product/index.html',
            {'categories': categories})

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
    if not products.exists():
        return HttpResponseNotFound()
    product = products[0].get_subtype_instance()
    context = {}
    response = []
    signals.product_view.send(
            sender=type(product), instance=product,
            request=request, response=response, extra_context=context
            )
    if len(response) == 1:
        return response[0]
    elif len(response) > 1:
        raise ValueError, _("Multiple responses returned.")
    print context
    context['product'] = product
    context['path'] = path
    return direct_to_template(request,
            'satchless/product/product.html',
            context)
