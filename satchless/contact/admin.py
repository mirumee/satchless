from django.contrib import admin
from . import models

class AddressInline(admin.StackedInline):
    model = models.Address

class CustomerAdmin(admin.ModelAdmin):
    inlines = [AddressInline]

admin.site.register(models.Customer, CustomerAdmin)
