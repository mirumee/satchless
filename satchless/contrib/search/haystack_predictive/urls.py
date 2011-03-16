# -*- coding:utf-8 -*-
from django.conf.urls.defaults import *

from . import forms
from . import views

urlpatterns = patterns('haystack.views',
    url(r'^$', views.search_product, name='satchless-search-haystack-predictive'),
)
