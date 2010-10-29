from django.conf.urls.defaults import *

urlpatterns = patterns('satchless.product.views',
        (r'^$', 'index'),
        (r'^(?P<parent_slugs>([a-z0-9_-]+/)*)(?P<category_slug>[a-z0-9_-]+)/$', 'category'),
        (r'^(?P<category_slugs>([a-z0-9_-]+/)+)\+(?P<product_slug>[a-z0-9_-]+)/$', 'product'),
        (r'^\+(?P<product_slug>[a-z0-9_-]+)/$', 'product'),
        )
