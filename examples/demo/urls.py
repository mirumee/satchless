from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from core.admin import gulliver_admin
import satchless.cart.views
from categories.app import product_app
from satchless.contrib.productset.app import productset_app
import core.views

urlpatterns = patterns('',
    url(r'^$', core.views.home_page, name='home-page'),
    url(r'^thankyou/(?P<order_token>\w+)/$', core.views.thank_you_page, name='thank-you'),
    url(r'^payment/failed/(?P<order_token>\w+)/$', core.views.payment_failed, name='payment-failed'),
    url(r'^products/', include(product_app.urls)),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^image/', include('satchless.image.urls')),
    url(r'^cart/view/(?P<typ>(satchless_cart|satchless_wishlist))/$',
         satchless.cart.views.cart, name='satchless-cart-view'),
    url(r'^cart/', include('satchless.cart.urls')),
    url(r'^carts/', include('carts.urls')),
    url(r'^order/', include('satchless.order.urls')),
    url(r'^checkout/', include('satchless.contrib.checkout.multistep.urls')),
    url(r'^product-set/', include(productset_app.urls)),
    url(r'^sale/', include('sale.urls')),
    url(r'^localeurl/', include('localeurl.urls')),
    url(r'^payment-gateways/django-payments/', include('payments.urls')),

    url(r'^search/', include('satchless.contrib.search.haystack_predictive.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(gulliver_admin.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
    )
