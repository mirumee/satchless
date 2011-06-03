from django.conf.urls.defaults import patterns, url

from ..common.urls import urlpatterns

from . import views

urlpatterns = urlpatterns + patterns('',
    url(r'^(?P<order_token>\w+)/$', views.checkout,
        name='satchless-checkout'),
    url(r'^(?P<order_token>\w+)/delivery-details/$', views.delivery_details,
        name='satchless-checkout-delivery-details'),
    url(r'^(?P<order_token>\w+)/payment-choice/$', views.payment_choice,
        name='satchless-checkout-payment-choice'),
    url(r'^(?P<order_token>\w+)/payment-details/$', views.payment_details,
        name='satchless-checkout-payment-details'),
    )
