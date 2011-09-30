from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404

from satchless.core.app import SatchlessApp
from satchless.product import handler

from . import models


class ProductSetApp(SatchlessApp):
    app_name = 'satchless-product-set'
    product_set_model = models.ProductSet

    def index_view(self, request, *args, **kwargs):
        """
        Show all product sets
        """
        sets = models.ProductSet.objects.all()
        return TemplateResponse(request, 'satchless/productset/index.html', {
            'sets': sets,
        })


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

    def get_urls(self, prefix=None):
        prefix = prefix or 'satchless-productset'
        return patterns('',
            url(r'^$',
                self.index_view,
                name=prefix),
            url(r'^(?P<slug>[a-z0-9_-]+)/$',
                self.details_view,
                name='%s-details' % (prefix,)),
        )

productset_app = ProductSetApp()
