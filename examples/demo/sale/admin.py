# -*- coding:utf-8 -*-
from django.contrib import admin

from . import models

class DiscountGroupAdmin(admin.ModelAdmin):
    model = models.DiscountGroup

admin.site.register(models.DiscountGroup, DiscountGroupAdmin)
