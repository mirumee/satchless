from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^$', views.checkout, {'typ': 'satchless_cart'}, name='satchless-checkout'),
    url(r'^delivery_details/$', views.delivery_details,
            name='satchless-checkout-delivery_details'),
    url(r'^payment_choice/$', views.payment_choice,
            name='satchless-checkout-payment_choice'),
    url(r'^payment_details/$', views.payment_details,
            name='satchless-checkout-payment_details'),
    url(r'^confirmation/$', views.confirmation,
            name='satchless-checkout-confirmation'),
    )
