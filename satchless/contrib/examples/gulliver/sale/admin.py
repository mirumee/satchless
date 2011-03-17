# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib import admin

import products.models
from . import models

class DiscountGroupAdmin(admin.ModelAdmin):
    model = models.DiscountGroup

admin.site.register(models.DiscountGroup, DiscountGroupAdmin)
