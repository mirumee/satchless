from django.conf.urls.defaults import patterns, url, include
import warnings

from . import app

warnings.warn('satchless.cart.urls is deprecated, use'
              ' satchless.cart.app.cart_app.urls instead')

urlpatterns = patterns('',
    url(r'', include(app.cart_app.urls)),
)
