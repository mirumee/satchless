from django.conf.urls.defaults import *
from . import views
from . import forms

urlpatterns = patterns('',
        # TODO
        # After http://code.djangoproject.com/ticket/13154 has been fixed, uncomment
        # the following line:
        #
        #url(r'^view/$', views.view_cart, {'typ': 'satchless.cart'}, name='satchless-cart-view'),
        #
        # ...and remove this:
        url(r'^view/(?P<typ>satchless\.cart)/$', views.view_cart, name='satchless-cart-view'),
        # ...stop removing here.
        url(r'^add/$', views.add_to_cart, {'typ': 'satchless.cart'}, name='satchless-cart-add'),
        )
