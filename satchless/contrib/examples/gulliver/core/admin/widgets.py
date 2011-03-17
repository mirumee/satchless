# -*- coding:utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
import django.forms

class ProductRawIdWidget(django.forms.TextInput):
    class Media:
        js = ('admin/js/relatedLookup.js', 'admin/js/lookupProduct.js')

    def render(self, *args, **kwargs):
        html = super(ProductRawIdWidget, self).render(*args, **kwargs)
        title = _("Search product id")
        button = ('<a class="related-lookup" href="%s" target="_blank">'
                  '<img width="16" height="16" alt="Lookup" src="%s" alt="%s" title="%s">'
                  '</a>') % (reverse('admin:search-products'),
                             settings.ADMIN_MEDIA_PREFIX + 'img/admin/selector-search.gif',
                             title, title)
        return html + mark_safe(button)

