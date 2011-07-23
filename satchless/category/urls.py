# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.CatgoryIndex(), name='satchless-category-index'),
    # this url simplifies url templatetag usage ({% url slug %} instead of {% url '' slug %})
    url(r'^(?P<category_slug>[a-z0-9_-]+)/$',
        views.CategoryDetails(), name='satchless-category-details',
        kwargs={'parent_slugs': ''}),
    url(r'^(?P<parent_slugs>([a-z0-9_-]+/)*)(?P<category_slug>[a-z0-9_-]+)/$',
        views.CategoryDetails(), name='satchless-category-details'),
    url(r'^(?P<category_slugs>([a-z0-9_-]+/)+)\+(?P<product_slug>[a-z0-9_-]+)/$',
        views.ProductDetails(), name='satchless-category-product-details'),
)
