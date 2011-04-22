# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^from-wishlist-to-cart/(?P<wishlist_item_id>\d+)/$',
        views.from_wishlist_to_cart,
        name='carts-from-wishlist-to-cart'),
)
