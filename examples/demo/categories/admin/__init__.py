# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms

from products.admin import ImageInline
from mptt.admin import MPTTModelAdmin

from .. import models
from . import fields


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ('name', 'slug', 'parent', 'description', 'meta_description')

    parent = fields.CategoryChoiceField(queryset=models.Category.objects.order_by('tree_id', 'lft'),
                                        required=False)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['parent'].queryset = (
                models.Category.objects
                    .exclude(
                            tree_id=self.instance.tree_id,
                            lft__gte=self.instance.lft,
                            rght__lte=self.instance.rght)
                    .order_by('tree_id', 'lft'))


class CategoryImageInline(ImageInline):
    model = models.CategoryImage


class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryImageInline]

admin.site.register(models.Category, CategoryAdmin)
