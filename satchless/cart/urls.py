from django.conf.urls.defaults import *
from . import views
from . import forms

urlpatterns = patterns('',
        # TODO
        # After http://code.djangoproject.com/ticket/13154 has been fixed, remove
        # the following line:
        url(r'^view/(?P<typ>satchless_cart)/$', views.cart, name='satchless-cart-view'),
        # ...stop removing here.
        url(r'^view/$', views.cart, {'typ': 'satchless_cart'}, name='satchless-cart-view'),
        )
