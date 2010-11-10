from django import forms
from django.conf import settings
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import fields
from . import models

class CategoryTranslationInline(admin.StackedInline):
    model = models.CategoryTranslation
    extra = 1
    max_num = len(settings.LANGUAGES) - 1

class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category

    parent = fields.CategoryChoiceField(queryset=models.Category.objects \
            .order_by('tree_id', 'lft'), required=False)

class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm
    inlines = (CategoryTranslationInline,)
    prepopulated_fields = {'slug': ('name',)}

class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product

    categories = fields.CategoryMultipleChoiceField(queryset=models.Category.objects \
            .order_by('tree_id', 'lft'), required=False)

class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(models.Category, CategoryAdmin)
