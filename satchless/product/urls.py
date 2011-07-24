# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    # '+' which predeces product slug prevents conflicts with categories paths
    url(r'^\+(?P<product_pk>[0-9]+)-(?P<product_slug>[a-z0-9_-]+)/$',
        views.ProductDetails(), name='satchless-product-details'),
)
