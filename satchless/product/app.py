from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from ..core.app import SatchlessApp, view

from . import models


class ProductApp(SatchlessApp):

    app_name = 'product'
    namespace = 'product'
    Product = None
    Variant = None
    product_view_handlers_queue = None

    def __init__(self, *args, **kwargs):
        super(ProductApp, self).__init__(*args, **kwargs)
        self.product_view_handlers_queue = set()
        assert self.Product, ('You need to subclass ProductApp and provide'
                              ' Product')
        assert self.Variant, ('You need to subclass ProductApp and provide'
                              ' Variant')

    def get_product(self, request, product_pk, product_slug):
        product = get_object_or_404(self.Product, pk=product_pk,
                                    slug=product_slug)
        return product.get_subtype_instance()

    def get_product_details_templates(self, product):
        return ['satchless/product/view.html']

    @view(r'^\+(?P<product_pk>[0-9]+)-(?P<product_slug>[a-z0-9_-]+)/$',
          name='details')
    def product_details(self, request, **kwargs):
        try:
            product = self.get_product(request, **kwargs)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
        context = self.on_product_view(instances=[product], request=request)
        if isinstance(context, HttpResponse):
            return context
        context['product'] = product
        context = self.get_context_data(request, **context)
        templates = self.get_product_details_templates(product)
        return TemplateResponse(request, templates, context)

    def register_product_view_handler(self, handler):
        self.product_view_handlers_queue.add(handler)

    def on_product_view(self, instances, request):
        context = {}
        for handler in self.product_view_handlers_queue:
            context = handler(instances, request=request, extra_context=context)
            if isinstance(context, HttpResponse):
                return context
        return context


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
