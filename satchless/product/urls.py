from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
        (r'^$', views.index),
        (r'^(?P<parent_slugs>([a-z0-9_-]+/)*)(?P<category_slug>[a-z0-9_-]+)/$', views.category),
        (r'^(?P<category_slugs>([a-z0-9_-]+/)+)\+(?P<product_slug>[a-z0-9_-]+)/$', views.product),
        (r'^\+(?P<product_slug>[a-z0-9_-]+)/$', views.product),
        )
