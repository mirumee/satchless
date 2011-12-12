# -*- coding:utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
import django.forms

#from satchless.contrib.productset.models import ProductSet, ProductSetItem
#from satchless.contrib.productset.admin import ProductSetImageInline

from sale.models import DiscountGroup
from categories.app import product_app
from search.haystack_predictive.views import search_products
from . import widgets

class DemoShopAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urls = super(DemoShopAdminSite, self).get_urls()
        urls += patterns('',
            url(r'^search/products/$', self.admin_view(search_products),
                kwargs={'template_name': 'admin/product/search_products.html'},
                name='search-products'),
        )
        return urls

demo_shop_admin = DemoShopAdminSite()

# FIXME (register by hand?): UGLY HACK to register apps in demo_shop_admin instance
admin.autodiscover()
for model, admin_class in admin.site._registry.items():
    if model not in (DiscountGroup,):#, ProductSet):
        demo_shop_admin.register(model, admin_class.__class__)

class DiscountProductForm(django.forms.ModelForm):
    product = django.forms.ModelChoiceField(label=_("variant id"),
                                            queryset=product_app.Product.objects.all(),
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

# FIXME: add product set application
#class ProductSetItemForm(django.forms.ModelForm):
#    variant = django.forms.ModelChoiceField(label=_("variant id"),
#                                            queryset=Variant.objects.all(),
#                                            widget=widgets.VariantRawIdWidget)
#    class Meta:
#        model = ProductSetItem
#
#class ProductSetItemInline(admin.TabularInline):
#    #form = ProductSetItemForm
#    model = ProductSetItem
#
#class ProductSetAdmin(admin.ModelAdmin):
#    prepopulated_fields = {'slug': ('name',)}
#    inlines = [ ProductSetItemInline, ProductSetImageInline, ]
#
#demo_shop_admin.register(ProductSet, ProductSetAdmin)
demo_shop_admin.register(DiscountGroup, DiscountGroupAdmin)
