from django.contrib import admin

from . import models


def make_country_action(region):
    name = 'add_to_region_%s' % region.pk
    action = lambda modeladmin, req, qset: qset.update(region=region)
    return (name, (action, name, "Add selected countries to '%s' region" % region.name))

class DeliveryCountryAdmin(admin.ModelAdmin):
    list_display = ('name','region','continent','code',)
    list_filter = ('region','continent',)
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': (
                            'name',
                            'region',
                            'promote',
                            )
        }),
    )
    ordering = ('name',)

    def get_actions(self, request):
        actions = super(DeliveryCountryAdmin, self).get_actions(request)
        actions.update(dict([make_country_action(region) for region in models.DeliveryRegion.objects.all()]))
        return actions

admin.site.register(models.DeliveryCountry, DeliveryCountryAdmin)


class PostShippingTypeAdmin(admin.ModelAdmin):
    list_display = ('region','name','description','price')
    list_filter = ('region',)
    search_fields = ('name','description')
    prepopulated_fields = {'typ': ('name',)}
    fieldsets = (
        (None, {'fields': (
                            'typ',
                            'name',
                            'description',
                            )
        }),
        (None, {'fields': (
                            'region',
                            'price',
                            )
        }),
    )
    ordering = ('region','price',)

admin.site.register(models.PostShippingType, PostShippingTypeAdmin)
admin.site.register(models.DeliveryRegion)