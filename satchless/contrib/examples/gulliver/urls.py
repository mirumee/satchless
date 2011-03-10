from django.conf import settings
from django.conf.urls.defaults import *
from core.forms import CartItemFormSet

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/products/'}),
    url(r'^products/', include('satchless.product.urls')),
    url(r'^contact/', include('satchless.contact.urls')),
    url(r'^image/', include('satchless.image.urls')),
    url(r'^view/(?P<typ>satchless_cart|satchless_wishlist)/$', 'satchless.cart.views.cart', name='satchless-cart-view'),
    url(r'^cart/', include('satchless.cart.urls'), {'formset_class': CartItemFormSet}),
    url(r'^order/', include('satchless.order.urls')),
    url(r'^product-set/', include('satchless.contrib.productset.urls')),
    url(r'^sale/', include('sale.urls')),
    url(r'^localeurl/', include('localeurl.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
                'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
    )
