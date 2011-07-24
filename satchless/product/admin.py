# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin

from . import models

class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product


# you should use satchless.category.admin.ProductAdmin if you are using category app
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    prepopulated_fields = {'slug': ('name',)}
