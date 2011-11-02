from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from core.admin import gulliver_admin
from carts.app import cart_app, wishlist_app
from categories.app import product_app
from orders.app import order_app
from satchless.contrib.productset.app import productset_app
from checkouts.app import checkout_app
import core.views

urlpatterns = patterns('',
    url(r'^$', core.views.home_page, name='home-page'),
    url(r'^thankyou/(?P<order_token>\w+)/$', core.views.thank_you_page, name='thank-you'),
    url(r'^payment/failed/(?P<order_token>\w+)/$', core.views.payment_failed, name='payment-failed'),
    url(r'^products/', include(product_app.urls)),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^image/', include('satchless.image.urls')),
    url(r'^cart/', include(cart_app.urls)),
    url(r'^wishlist/', include(wishlist_app.urls)),
    url(r'^order/', include(order_app.urls)),
    url(r'^checkout/', include(checkout_app.urls)),
    url(r'^product-set/', include(productset_app.urls)),
    url(r'^sale/', include('sale.urls')),
    url(r'^localeurl/', include('localeurl.urls')),
    url(r'^payment-gateways/django-payments/', include('payments.urls')),
    url(r'^search/', include('search.haystack_predictive.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(gulliver_admin.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
    )
