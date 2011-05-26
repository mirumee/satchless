from django.conf.urls.defaults import url, patterns

from ..common.views import prepare_order, confirmation
from . import views

urlpatterns = patterns('',
    url(r'^(?P<order_token>\w+)/$', views.checkout,
        name='satchless-checkout'),
    url(r'^prepare-order/$', prepare_order, {'typ': 'satchless_cart'},
        name='satchless-checkout-prepare-order'),
    url(r'^(?P<order_token>\w+)/delivery-details/$', views.delivery_details,
        name='satchless-checkout-delivery-details'),
    url(r'^(?P<order_token>\w+)/payment-choice/$', views.payment_choice,
        name='satchless-checkout-payment-choice'),
    url(r'^(?P<order_token>\w+)/payment-details/$', views.payment_details,
        name='satchless-checkout-payment-details'),
    url(r'^(?P<order_token>\w+)/confirmation/$', confirmation,
        name='satchless-checkout-confirmation'),
    )
