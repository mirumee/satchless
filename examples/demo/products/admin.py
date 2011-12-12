# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from django.conf import settings
import django.db.models
from django.db.models.query import EmptyQuerySet

from categories.app import product_app
import pricing.models
import sale.models
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
    categories = CategoryMultipleChoiceField(queryset=product_app.Category.objects
                                             .order_by('tree_id', 'lft'), required=False)
    class Meta:
        model = product_app.Product

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['categories'].initial = [c.id for c in self.instance.categories.all()]
        if self.instance.id:
            self.fields['main_image'].queryset = (models.ProductImage.objects
                                                        .filter(product=self.instance))
        else:
            self.fields['main_image'].queryset = EmptyQuerySet(model=models.ProductImage)

    def _save_categories(self, instance):
        categories = self.cleaned_data['categories']
        categories_for_removal = set(instance.categories.all())
        for category in categories:
            instance.categories.add(category)
            if category in categories_for_removal:
                categories_for_removal.remove(category)
        for category in categories_for_removal:
            instance.categories.remove(category)

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=commit)
        if commit:
            self._update_categories(instance)
        return instance


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    prepopulated_fields = {'slug': ('name',)}

    def save_model(self, request, obj, form, change):
        obj.save()
        form._save_categories(obj)


class ProductImageInline(ImageInline):
    extra = 4
    max_num = 4
    model = models.ProductImage
    sortable_field_name = "order"


class PriceInline(admin.TabularInline):
    model = pricing.models.ProductPrice
    #form = .pricing.simpleqty.admin.ProductPriceForm


class DiscountInline(admin.TabularInline):
    model = sale.models.DiscountGroup.products.through
    max_num = 1


class CardiganVariantInline(admin.TabularInline):
    model = models.CardiganVariant


class CardiganTranslationInline(TranslationInline):
    model = models.CardiganTranslation


class CardiganAdmin(ProductAdmin):
    inlines = [CardiganTranslationInline, CardiganVariantInline, PriceInline,
               DiscountInline, ProductImageInline]


class DressVariantInline(admin.TabularInline):
    model = models.DressVariant


class DressTranslationInline(TranslationInline):
    model = models.DressTranslation


class DressAdmin(ProductAdmin):
    inlines = [DressTranslationInline, DressVariantInline, PriceInline,
               DiscountInline, ProductImageInline]


class HatTranslationInline(TranslationInline):
    model = models.HatTranslation


class HatAdmin(ProductAdmin):
    inlines = [HatTranslationInline, DiscountInline, PriceInline,
               ProductImageInline]


class JacketVariantInline(admin.TabularInline):
    model = models.JacketVariant


class JacketTranslationInline(TranslationInline):
    model = models.JacketTranslation


class JacketAdmin(ProductAdmin):
    inlines = [JacketTranslationInline, DiscountInline, PriceInline,
               JacketVariantInline, ProductImageInline]


class ShirtVariantInline(admin.TabularInline):
    model = models.ShirtVariant


class ShirtTranslationInline(TranslationInline):
    model = models.ShirtTranslation


class ShirtAdmin(ProductAdmin):
    inlines = [ShirtTranslationInline, ShirtVariantInline,
               DiscountInline, ProductImageInline, PriceInline]


class TrousersVariantInline(admin.TabularInline):
    model = models.TrousersVariant


class TrousersTranslationInline(TranslationInline):
    model = models.TrousersTranslation


class TrousersAdmin(ProductAdmin):
    inlines = [TrousersTranslationInline, TrousersVariantInline,
               DiscountInline, ProductImageInline, PriceInline]


class TShirtVariantInline(admin.TabularInline):
    model = models.TShirtVariant


class TShirtTranslationInline(TranslationInline):
    model = models.TShirtTranslation


class TShirtAdmin(ProductAdmin):
    inlines = [TShirtTranslationInline, TShirtVariantInline,
               DiscountInline, ProductImageInline, PriceInline]


admin.site.register(models.Cardigan, CardiganAdmin)
admin.site.register(models.Dress, DressAdmin)
admin.site.register(models.Hat, HatAdmin)
admin.site.register(models.Jacket, JacketAdmin)
admin.site.register(models.Shirt, ShirtAdmin)
admin.site.register(models.Trousers, TrousersAdmin)
admin.site.register(models.TShirt, TShirtAdmin)

admin.site.register(models.Make)
