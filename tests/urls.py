# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url, include

from satchless.category.app import product_app as category_app
from satchless.product.app import product_app
from satchless.order.app import order_app

urlpatterns = patterns('',
    url(r'^category/', include(category_app.urls)),
    url(r'^product/', include(product_app.urls)),
    url(r'^cart/', include('satchless.cart.urls')),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^order/', include(order_app.get_urls())),
    url(r'^image/', include('satchless.image.urls')),
)
