from django.conf import settings
from django.contrib import admin

from . import models

class PostShippingTypeTranslationInline(admin.TabularInline):
    model = models.PostShippingTypeTranslation
    extra = 1
    max_num = len(settings.LANGUAGES) - 1

class PostShippingTypeAdmin(admin.ModelAdmin):
    model = models.PostShippingType
    inlines = [PostShippingTypeTranslationInline]
    list_display = ('name',)
    prepopulated_fields = {'typ': ('name',)}

admin.site.register(models.PostShippingType, PostShippingTypeAdmin)
