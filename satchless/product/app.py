from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..core.app import SatchlessApp

from . import models
from . import handler

class ProductApp(SatchlessApp):
    app_name = 'satchless-product'
    product_model = models.Product
    product_details_templates = [
        'satchless/product/%(product_app)s/%(product_model)s/view.html',
        'satchless/product/%(product_app)s/view.html',
        'satchless/product/view.html',
    ]

    def get_template_names(self, product, **kwargs):
        product_data = {
            'product_app': product._meta.module_name,
            'product_model': product._meta.object_name.lower(),
        }
        return [t % product_data for t in self.product_details_templates]

    def get_product(self, request, product_pk, product_slug):
        product = get_object_or_404(self.product_model, pk=product_pk,
                                    slug=product_slug)
        return product.get_subtype_instance()

    def get_context_data(self, request, **kwargs):
        return kwargs

    def product_details(self, request, **kwargs):
        product = self.get_product(request, **kwargs)
        context = handler.product_view(instances=[product], request=request)
        if isinstance(context, HttpResponse):
            return context
        context['product'] = product
        context = self.get_context_data(request, **context)
        return self.respond(request, context, product=product)

    def get_urls(self, prefix=None):
        prefix = prefix or 'satchless-product'
        return patterns('',
            # '+' predeces product slug to prevent conflicts with categories
            # paths
            url(r'^\+(?P<product_pk>[0-9]+)-(?P<product_slug>[a-z0-9_-]+)/$',
                self.product_details, name='%s-details' % prefix),
        )

product_app = ProductApp()
