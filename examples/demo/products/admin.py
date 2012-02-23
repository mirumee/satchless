# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _, ugettext
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


class HatForm(ProductForm, forms.ModelForm):
    stock_level = forms.DecimalField(max_digits=10, min_value=0)
    sku = forms.CharField()

    class Meta:
        model = models.Hat

    def __init__(self, *args, **kwargs):
        super(HatForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            variant = self.instance.variants.get()
            self.fields['stock_level'].initial = variant.stock_level
            self.fields['sku'].initial = variant.sku

    def clean_sku(self):
        sku = self.cleaned_data.get('sku', None)
        if sku is not None:
            query = Q(sku=sku)
            if self.instance.id:
                query &= ~Q(id=self.instance.variants.get().id)
            if models.Variant.objects.filter(query).exists():
                raise ValidationError(ugettext('Sku is not unique'))
        return sku


singlevariant_product_fieldsets = (
    (_('General'), {
        'fields': ('name', 'slug', 'description', 'main_image')
    }),
    (_('Pricing'), {
        'fields': ('price', 'tax_group', 'discount'),
    }),
    (_('Stock'), {
        'fields': ('sku', 'stock_level',),
    }),
    (_('Categories'), {
        'fields': ('categories',),
    }),
)

class HatAdmin(ProductAdmin):
    inlines = [HatTranslationInline,
               PriceQtyOverrideInline, ProductImageInline]
    fieldsets = singlevariant_product_fieldsets
    form = HatForm

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.variants.exists():
            variant = obj.variants.get()
        else:
            variant = models.HatVariant(product=obj)
        variant.stock_level = form.cleaned_data['stock_level']
        variant.sku = form.cleaned_data['sku']
        variant.save()


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
