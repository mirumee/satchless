from django.conf.urls.defaults import url, patterns

from ..common.views import prepare_order, confirmation
from . import views

urlpatterns = patterns('',
    url(r'^$', views.checkout, {'typ': 'satchless_cart'},
        name='satchless-checkout'),
    url(r'^prepare-order/$', prepare_order, {'typ': 'satchless_cart'},
        name='satchless-checkout-prepare-order'),
    url(r'^delivery-details/$', views.delivery_details,
        name='satchless-checkout-delivery-details'),
    url(r'^payment-choice/$', views.payment_choice,
        name='satchless-checkout-payment-choice'),
    url(r'^payment-details/$', views.payment_details,
        name='satchless-checkout-payment-details'),
    url(r'^confirmation/$', confirmation,
        name='satchless-checkout-confirmation'),
    )
