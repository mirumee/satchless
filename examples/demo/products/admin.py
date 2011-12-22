# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from django.conf import settings
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _
import django.db.models

from categories.app import product_app
import pricing.models
from . import widgets
from . import models

from categories.admin.fields import CategoryMultipleChoiceField


class TranslationInline(admin.StackedInline):
    extra = 1
    max_num = len(settings.LANGUAGES) - 1


class ImageInline(admin.TabularInline):
    formfield_overrides = {
        django.db.models.ImageField: { 'widget': widgets.AdminImageWidget },
    }


class ProductForm(forms.ModelForm):
    categories = CategoryMultipleChoiceField(required=False,
                                             queryset=product_app.Category.objects
                                                                          .order_by('tree_id',
                                                                                    'lft'))
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['main_image'].queryset = self.instance.images.all()

product_fieldsets = (
    (_('General'), {
        'fields': ('name', 'slug', 'description', 'main_image')
    }),
    (_('Pricing'), {
        'fields': ('price', 'qty_mode', 'tax_group', 'discount'),
    }),
    (_('Categories'), {
        'fields': ('categories',),
    }),
)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(ImageInline):
    extra = 4
    max_num = 4
    model = models.ProductImage
    sortable_field_name = "order"


class PriceQtyOverrideInline(admin.TabularInline):
    model = pricing.models.PriceQtyOverride


class CardiganVariantInline(admin.TabularInline):
    model = models.CardiganVariant


class CardiganTranslationInline(TranslationInline):
    model = models.CardiganTranslation


class CardiganAdmin(ProductAdmin):
    model = models.Cardigan
    form = modelform_factory(models.Cardigan, form=ProductForm)
    inlines = [CardiganTranslationInline, CardiganVariantInline,
               PriceQtyOverrideInline, ProductImageInline]
    fieldsets = product_fieldsets


class DressVariantInline(admin.TabularInline):
    model = models.DressVariant


class DressTranslationInline(TranslationInline):
    model = models.DressTranslation


class DressAdmin(ProductAdmin):
    inlines = [DressTranslationInline, DressVariantInline,
               PriceQtyOverrideInline, ProductImageInline]
    form = modelform_factory(models.Dress, form=ProductForm)
    fieldsets = product_fieldsets


class HatTranslationInline(TranslationInline):
    model = models.HatTranslation


class HatAdmin(ProductAdmin):
    inlines = [HatTranslationInline, PriceQtyOverrideInline,
               ProductImageInline]
    fieldsets = product_fieldsets
    form = modelform_factory(models.Hat, form=ProductForm)


class JacketVariantInline(admin.TabularInline):
    model = models.JacketVariant


class JacketTranslationInline(TranslationInline):
    model = models.JacketTranslation


class JacketAdmin(ProductAdmin):
    inlines = [JacketTranslationInline, PriceQtyOverrideInline,
               JacketVariantInline, ProductImageInline]
    fieldsets = product_fieldsets
    form = modelform_factory(models.Jacket, form=ProductForm)


class ShirtVariantInline(admin.TabularInline):
    model = models.ShirtVariant


class ShirtTranslationInline(TranslationInline):
    model = models.ShirtTranslation


class ShirtAdmin(ProductAdmin):
    inlines = [ShirtTranslationInline, ShirtVariantInline,
               ProductImageInline, PriceQtyOverrideInline]
    fieldsets = product_fieldsets
    form = modelform_factory(models.Shirt, form=ProductForm)


class TrousersVariantInline(admin.TabularInline):
    model = models.TrousersVariant


class TrousersTranslationInline(TranslationInline):
    model = models.TrousersTranslation


class TrousersAdmin(ProductAdmin):
    inlines = [TrousersTranslationInline, TrousersVariantInline,
               ProductImageInline, PriceQtyOverrideInline]
    fieldsets = product_fieldsets
    form = modelform_factory(models.Trousers, form=ProductForm)


class TShirtVariantInline(admin.TabularInline):
    model = models.TShirtVariant


class TShirtTranslationInline(TranslationInline):
    model = models.TShirtTranslation


class TShirtAdmin(ProductAdmin):
    inlines = [TShirtTranslationInline, TShirtVariantInline,
               ProductImageInline, PriceQtyOverrideInline]
    fieldsets = product_fieldsets
    form = modelform_factory(models.TShirt, form=ProductForm)


admin.site.register(models.Cardigan, CardiganAdmin)
admin.site.register(models.Dress, DressAdmin)
admin.site.register(models.Hat, HatAdmin)
admin.site.register(models.Jacket, JacketAdmin)
admin.site.register(models.Shirt, ShirtAdmin)
admin.site.register(models.Trousers, TrousersAdmin)
admin.site.register(models.TShirt, TShirtAdmin)

admin.site.register(models.Make)
