from django.conf.urls.defaults import patterns, url, include
import warnings

from . import app

warnings.warn('satchless.category.urls is deprecated, use'
              ' satchless.category.app.product_app.urls instead')

urlpatterns = patterns('',
    url(r'', include(app.product_app.urls)),
)
