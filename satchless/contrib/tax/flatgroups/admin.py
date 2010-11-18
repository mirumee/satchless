from django.contrib import admin
from . import models

class TaxGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate_name', 'default')

admin.site.register(models.TaxGroup, TaxGroupAdmin)
