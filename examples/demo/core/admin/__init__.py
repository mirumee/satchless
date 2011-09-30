# -*- coding:utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
import django.forms

from satchless.contrib.productset.models import ProductSet, ProductSetItem
from satchless.contrib.productset.admin import ProductSetImageInline
from satchless.contrib.search.haystack_predictive.views import search_products
from satchless.product.models import Product, Variant

from sale.models import DiscountGroup
from . import widgets

class GulliverAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urls = super(GulliverAdminSite, self).get_urls()
        urls += patterns('',
            url(r'^search/products/$', self.admin_view(search_products),
                kwargs={'template_name': 'admin/product/search_products.html'},
                name='search-products'),
        )
        return urls

gulliver_admin = GulliverAdminSite()

# FIXME (register by hand?): UGLY HACK to register apps in gulliver_admin instance
admin.autodiscover()
for model, admin_class in admin.site._registry.items():
    if model not in (DiscountGroup, ProductSet):
        gulliver_admin.register(model, admin_class.__class__)

class DiscountProductForm(django.forms.ModelForm):
    product = django.forms.ModelChoiceField(label=_("variant id"),
                                            queryset=Product.objects.all(),
                                            widget=widgets.ProductRawIdWidget)
    class Meta:
        model = DiscountGroup.products.through

class DiscountProductInline(admin.TabularInline):
    model = DiscountGroup.products.through
    form = DiscountProductForm

class DiscountGroupAdmin(admin.ModelAdmin):
    model = DiscountGroup
    inlines = [ DiscountProductInline, ]
    exclude = ('products',)

class ProductSetItemForm(django.forms.ModelForm):
    variant = django.forms.ModelChoiceField(label=_("variant id"),
                                            queryset=Variant.objects.all(),
                                            widget=widgets.VariantRawIdWidget)
    class Meta:
        model = ProductSetItem

class ProductSetItemInline(admin.TabularInline):
    #form = ProductSetItemForm
    model = ProductSetItem

class ProductSetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ ProductSetItemInline, ProductSetImageInline, ]

gulliver_admin.register(ProductSet, ProductSetAdmin)
gulliver_admin.register(DiscountGroup, DiscountGroupAdmin)
