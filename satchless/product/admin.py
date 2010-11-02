from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import models

class CategoryAdmin(MPTTModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(models.Category, CategoryAdmin)
