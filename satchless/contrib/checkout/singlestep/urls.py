from django.conf.urls.defaults import patterns, url

from ..common.views import prepare_order, confirmation
from . import views

urlpatterns = patterns('',
    url(r'^(?P<order_token>\w+)/$', views.checkout,
        name='satchless-checkout'),
    url(r'^prepare-order/$', prepare_order, {'typ': 'satchless_cart'},
        name='satchless-checkout-prepare-order'),
    url(r'^(?P<order_token>\w+)/confirmation/$', confirmation,
        name='satchless-checkout-confirmation'),
    )
