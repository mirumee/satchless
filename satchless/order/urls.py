from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^checkout/$', views.checkout, {'typ': 'satchless_cart'}, name='satchless-checkout'),
    )
