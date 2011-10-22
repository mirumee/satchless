from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from ..core.app import SatchlessApp

from . import models
from . import handler

class ProductApp(SatchlessApp):
    app_name = 'product'
    namespace = 'product'
    product_model = models.Product
    product_details_templates = [
        'satchless/product/%(product_model)s/view.html',
        'satchless/product/view.html',
    ]

    def get_product(self, request, product_pk, product_slug):
        product = get_object_or_404(self.product_model, pk=product_pk,
                                    slug=product_slug)
        return product.get_subtype_instance()

    def product_details(self, request, **kwargs):
        product = self.get_product(request, **kwargs)
        context = handler.product_view(instances=[product], request=request)
        if isinstance(context, HttpResponse):
            return context
        context['product'] = product
        context = self.get_context_data(request, **context)
        product_data = {
            'product_model': product._meta.module_name,
        }
        templates = [t % product_data for t in self.product_details_templates]
        return TemplateResponse(request, templates, context)

    def get_urls(self):
        return patterns('',
            # '+' predeces product slug to prevent conflicts with categories
            # paths
            url(r'^\+(?P<product_pk>[0-9]+)-(?P<product_slug>[a-z0-9_-]+)/$',
                self.product_details, name='details'),
        )

product_app = ProductApp()