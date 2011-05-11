from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.checkout, {'typ': 'satchless_cart'}, name='satchless-checkout'),
    url(r'^order-from-cart/$', views.order_from_cart, {'typ': 'satchless_cart'},
        name='satchless-order-from-cart'),
    url(r'^confirmation/$', 'satchless.contrib.checkout.full.views.confirmation',
        name='satchless-checkout-confirmation'),
    )
