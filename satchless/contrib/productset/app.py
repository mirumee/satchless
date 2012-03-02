from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404

from ...core.app import SatchlessApp, view
from ...product import handler
from . import models

class ProductSetApp(SatchlessApp):
    app_name = 'product-set'
    namespace = 'product-set'
    product_set_model = models.ProductSet

    @view(r'^$', name='index')
    def index(self, request, *args, **kwargs):
        """
        Show all product sets
        """
        sets = models.ProductSet.objects.all()
        return TemplateResponse(request, 'satchless/productset/index.html', {
            'sets': sets,
        })

    @view(r'^(?P<slug>[a-z0-9_-]+)/$', name='details')
    def details_view(self, request, slug):
        """
        Show a list of products with coresponding add-to-cart forms
        """
        productset = get_object_or_404(models.ProductSet, slug=slug)
        variant_instances = productset.variant_instances()
        context = handler.product_view(instances=variant_instances, request=request)
        if isinstance(context, HttpResponse):
            return context
        context['variants'] = variant_instances
        context['productset'] = productset
        return TemplateResponse(request, 'satchless/productset/details.html',
                                context)