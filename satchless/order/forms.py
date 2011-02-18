from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from .handler import get_delivery_types
from . import models

class DeliveryMethodForm(forms.ModelForm):
    delivery_typ = forms.ChoiceField(label=_('Delivery method'), choices=[])

    class Meta:
        model = models.DeliveryGroup
        fields = ('delivery_typ',)

    def __init__(self, *args, **kwargs):
        super(DeliveryMethodForm, self).__init__(*args, **kwargs)
        self.fields['delivery_typ'].choices = get_delivery_types(self.instance)

DeliveryMethodFormset = modelformset_factory(models.DeliveryGroup, form=DeliveryMethodForm, extra=0)
