from django.conf.urls.defaults import patterns, include, url

from ..app import CategorizedProductApp

class CategorizedProductAppWithOrphans(CategorizedProductApp):
    """A CategorizedProductApp that allows Products not in Categories"""

    allow_uncategorized_product_urls = True

urlpatterns = patterns('',
    url(r'^products/', include(CategorizedProductAppWithOrphans().get_urls())),
)


from .category import *
