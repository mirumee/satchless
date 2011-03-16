# -*- coding:utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse, Http404
from django.views.generic.simple import direct_to_template

from haystack.query import EmptySearchQuerySet, RelatedSearchQuerySet

from satchless.product.models import Product, Variant
from satchless.contrib.search.haystack_predictive.views import search_products

class GulliverAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urls = super(GulliverAdminSite, self).get_urls()
        urls += patterns('',
            url(r'^search/product/$', self.admin_view(search_products),
                kwargs={'template_name': 'admin/product/search_products.html'},
                name='search-products')
        )
        return urls

gulliver_admin = GulliverAdminSite()

# FIXME: UGLY HACK to register apps admins
from django.contrib import admin
admin.autodiscover()

for model, admin_class in admin.site._registry.items():
    gulliver_admin.register(model, admin_class.__class__)
