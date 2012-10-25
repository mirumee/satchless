# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.sales, name='sale'),
    url(r'^(?P<category_slugs>(([a-z0-9_-]+/)*[a-z0-9_-]+))/$',
        views.sales, name='sale'),
)
