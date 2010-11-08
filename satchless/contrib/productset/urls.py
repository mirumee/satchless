from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'(?P<slug>[a-z0-9_-]+)/$', views.details, name='satchless-product-set'),
    url(r'$', views.index, name='satchless-product-set-index'),
)
