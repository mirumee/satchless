from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^my-orders/$', views.my_orders, name='satchless-order-my-orders'),
    url(r'^(?P<order_pk>[0-9]+)/$', views.view, name='satchless-order-view'),
    )
