from django.conf.urls.defaults import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.checkout, {'typ': 'satchless_cart'}, name='satchless-checkout'),
    url(r'^prepare-order/$', views.prepare_order, {'typ': 'satchless_cart'},
        name='satchless-checkout-prepare-order'),
    url(r'^confirmation/$', 'satchless.contrib.checkout.multistep.views.confirmation',
        name='satchless-checkout-confirmation'),
    )
