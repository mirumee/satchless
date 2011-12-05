from django import forms
from django.utils.safestring import mark_safe

from satchless.util.fields import GroupedModelChoiceField

from . import models


class PostShippingVariantForm(forms.ModelForm):
    class Meta:
        model = models.PostShippingVariant
        exclude = ('delivery_group', 'name', 'description', 'price')


# not used - for selecting option pre delivery address
class DeliveryChoiceField(GroupedModelChoiceField):
    def __init__(self, *args, **kwargs):
        super(DeliveryChoiceField, self).__init__(
            *args,
            group_by_field='region',
            group_label=lambda region: '%s:' % region.name,
            required=False,
            queryset=models.PostShippingType.objects.all(),
            widget=forms.Select,
            **kwargs
        )

    def label_from_instance(self, obj):
        # TODO: satchless needs a way of handling currency codes/symbols
        return mark_safe('%s ... &pound;%s' % (obj.name, obj.cost))

class DeliveryForm(forms.Form):
    delivery = DeliveryChoiceField(empty_label='Please select')