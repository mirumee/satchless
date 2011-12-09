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
    Product = None
    Variant = None
    product_details_templates = [
        'satchless/product/%(product_model)s/view.html',
        'satchless/product/view.html',
    ]

    def __init__(self, *args, **kwargs):
        super(ProductApp, self).__init__(*args, **kwargs)
        assert self.Product, ('You need to subclass ProductApp and provide'
                              ' Product')
        assert self.Variant, ('You need to subclass ProductApp and provide'
                              ' Variant')

    def get_product(self, request, product_pk, product_slug):
        product = get_object_or_404(self.Product, pk=product_pk,
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


class MagicProductApp(ProductApp):

    def __init__(self, **kwargs):
        self.Product = (self.Product or
                        self.construct_product_class())
        self.Variant = (self.Variant or
                        self.construct_variant_class(self.Product))
        super(MagicProductApp, self).__init__(**kwargs)

    def construct_product_class(self):
        class Product(models.Product):
            pass
        return Product

    def construct_variant_class(self, product_class):
        class Variant(models.Variant):
            pass
        return Variant