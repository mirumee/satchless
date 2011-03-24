from django import forms
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import fields
from . import models

class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category

    parent = fields.CategoryChoiceField(queryset=models.Category.objects \
            .order_by('tree_id', 'lft'), required=False)

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

class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product

    categories = fields.CategoryMultipleChoiceField(queryset=models.Category.objects \
            .order_by('tree_id', 'lft'), required=False)

class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(models.Category, CategoryAdmin)
