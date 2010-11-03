from django.contrib import admin
from . import models

class AddressInline(admin.StackedInline):
    model = models.Address
    prepopulated_fields = {'alias': ('street_address_1', 'city')}

class CustomerAdmin(admin.ModelAdmin):
    inlines = [AddressInline]

admin.site.register(models.Customer, CustomerAdmin)
