from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^(?P<order_pk>[0-9]+)/$', views.view, name='satchless-order-view'),
    url(r'^checkout/$', views.checkout, {'typ': 'satchless_cart'}, name='satchless-checkout'),
    url(r'^checkout/delivery_details/$', views.delivery_details,
            name='satchless-checkout-delivery_details'),
    url(r'^checkout/payment_choice/$', views.payment_choice,
            name='satchless-checkout-payment_choice'),
    url(r'^checkout/payment_details/$', views.payment_details,
            name='satchless-checkout-payment_details'),
    url(r'^checkout/confirmation/$', views.confirmation,
            name='satchless-checkout-confirmation'),
    )
