from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from satchless.product import signals

from . import models

def index(request, *args, **kwargs):
    """Show all sets"""
    pass

def details(request, slug):
    """
    Show product set
    """
    print "slug: " + slug
    productset = get_object_or_404(models.ProductSet, slug=slug)
    context = {}
    response = []
    variant_instances = productset.variant_instances()
    print len(variant_instances)
    signals.product_view.send(
                sender=type(productset), instances=variant_instances,
                request=request, response=response, extra_context=context)
    if len(response) == 1:
        return response[0]
    elif len(response) > 1:
        raise ValueError, "Multiple responses returned."
    context['variants'] = variant_instances
    context['productset'] = productset
    return direct_to_template(request,
            'satchless/productset/details.html',
            context)
