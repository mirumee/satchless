# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^product/', include('satchless.product.urls')),
    url(r'^cart/', include('satchless.cart.urls')),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^image/', include('satchless.image.urls')),
)
