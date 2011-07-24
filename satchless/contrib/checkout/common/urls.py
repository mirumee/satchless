# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

from .views import confirmation, prepare_order, reactivate_order

urlpatterns = patterns('',
    url(r'^prepare/$', prepare_order, {'typ': 'satchless_cart'},
        name='satchless-checkout-prepare-order'),
    url(r'^(?P<order_token>\w+)/confirmation/$', confirmation,
        name='satchless-checkout-confirmation'),
    url(r'^(?P<order_token>\w+)/reactivate/$', reactivate_order,
        name='satchless-checkout-reactivate-order'),
    )
