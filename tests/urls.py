# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^product/', include('satchless.product.urls')),
    url(r'^cart/', include('satchless.cart.urls')),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^image/', include('satchless.image.urls')),
    url(r'^checkout/multistep/', include('satchless.contrib.checkout.multistep.urls')),
    url(r'^checkout/singlestep/', include('satchless.contrib.checkout.singlestep.urls', app_name='singlestep')),
)
