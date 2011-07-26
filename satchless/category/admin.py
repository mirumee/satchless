# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms

from mptt.admin import MPTTModelAdmin

from ..product.models import Product
from . import fields
from . import models

class ProductForm(forms.ModelForm):
    categories = fields.CategoryMultipleChoiceField(queryset=models.Category.objects \
                                                    .order_by('tree_id', 'lft'), required=False)
    class Meta:
        model = Product

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['categories'].initial = [c.id for c in self.instance.categories.all()]

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


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ('name', 'slug', 'parent', 'description', 'meta_description', 'products',)

    parent = fields.CategoryChoiceField(queryset=models.Category.objects.order_by('tree_id', 'lft'),
                                        required=False)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['parent'].queryset = models.Category.objects\
                    .exclude(
                            tree_id=self.instance.tree_id,
                            lft__gte=self.instance.lft,
                            rght__lte=self.instance.rght)\
                    .order_by('tree_id', 'lft')


class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(models.Category, CategoryAdmin)
