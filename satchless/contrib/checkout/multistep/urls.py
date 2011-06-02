from django.conf.urls.defaults import patterns, url

from ..common.views import confirmation, prepare_order, reactivate_order
from . import views

urlpatterns = patterns('',
    url(r'^prepare/$', prepare_order, {'typ': 'satchless_cart'},
        name='satchless-checkout-prepare-order'),
    url(r'^(?P<order_token>\w+)/$', views.checkout,
        name='satchless-checkout'),
    url(r'^(?P<order_token>\w+)/confirmation/$', confirmation,
        name='satchless-checkout-confirmation'),
    url(r'^(?P<order_token>\w+)/delivery-details/$', views.delivery_details,
        name='satchless-checkout-delivery-details'),
    url(r'^(?P<order_token>\w+)/payment-choice/$', views.payment_choice,
        name='satchless-checkout-payment-choice'),
    url(r'^(?P<order_token>\w+)/payment-details/$', views.payment_details,
        name='satchless-checkout-payment-details'),
    url(r'^(?P<order_token>\w+)/reactivate/$', reactivate_order,
        name='satchless-checkout-reactivate-order'),
    )
