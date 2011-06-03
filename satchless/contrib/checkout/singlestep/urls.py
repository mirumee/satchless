from django.conf.urls.defaults import patterns, url

from ..common.urls import urlpatterns

from . import views

urlpatterns = urlpatterns + patterns('',
    url(r'^(?P<order_token>\w+)/$', views.checkout,
        name='satchless-checkout'),
    )

