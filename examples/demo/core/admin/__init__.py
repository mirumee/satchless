# -*- coding:utf-8 -*-
from django.contrib import admin

from search.haystack_predictive.views import search_products

class DemoShopAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urls = super(DemoShopAdminSite, self).get_urls()
        urls += patterns('',
            url(r'^search/products/$', self.admin_view(search_products),
                kwargs={'template_name': 'admin/product/search_products.html'},
                name='search-products'),
        )
        return urls

demo_shop_admin = DemoShopAdminSite()

# FIXME: UGLY HACK to register apps in demo_shop_admin instance
admin.autodiscover()
for model, admin_class in admin.site._registry.items():
    demo_shop_admin.register(model, admin_class.__class__)

