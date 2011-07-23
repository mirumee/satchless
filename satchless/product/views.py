# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from scbv.views import View

from . import models
from . import handler

class ProductDetails(View):
    def get_template_names(self, product, **kwargs):
        return [
            'satchless/product/%s/%s/view.html' %
            (product._meta.module_name, product._meta.object_name.lower()),
            'satchless/product/%s/view.html' % product._meta.module_name,
            'satchless/product/view.html',
        ]

    def get_product(self, request, product_pk, product_slug):
        product = get_object_or_404(models.Product, pk=product_pk,
                                    slug=product_slug)
        return product.get_subtype_instance()

    def get_context_data(self, request, **kwargs):
        return kwargs

    def __call__(self, request, **kwargs):
        product = self.get_product(request, **kwargs)
        context = handler.product_view(instances=[product], request=request)
        if isinstance(context, HttpResponse):
            return context
        context['product'] = product
        context = self.get_context_data(request, **context)
        return self.respond(request, context, product=product)
