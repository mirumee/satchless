from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^my-orders/$', views.my_orders, name='satchless-order-my-orders'),
    url(r'^(?P<order_token>[0-9a-zA-Z]+)/$', views.view, name='satchless-order-view'),
    )
