from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
        # TODO
        # After http://code.djangoproject.com/ticket/13154 has been fixed, remove
        # the following lines:
        url(r'^view/(?P<typ>satchless_cart)/$', views.cart, name='satchless-cart-view'),
        url(r'^remove/(?P<typ>satchless_cart)/(?P<item_pk>[0-9]+)/$',
            views.remove_item, name='satchless-cart-remove-item'),
        # ...stop removing here.
        url(r'^view/$', views.cart, {'typ': 'satchless_cart'}, name='satchless-cart-view'),
        url(r'^remove/(?P<item_pk>[0-9]+)/$', views.remove_item,
            {'typ': 'satchless_cart'}, name='satchless-cart-remove-item'),
        )
