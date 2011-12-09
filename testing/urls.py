# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url, include

from satchless.cart.tests import cart_app
from satchless.category.tests import category_app
from satchless.product.tests import product_app
from satchless.order.tests import order_app

urlpatterns = patterns('',
    url(r'^category/', include(category_app.urls)),
    url(r'^product/', include(product_app.urls)),
    url(r'^cart/', include(cart_app.urls)),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^order/', include(order_app.urls)),
    url(r'^image/', include('satchless.image.urls')),
)