from django import forms
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.translation import ugettext as _

from . import handler
from . import models

class DeliveryMethodForm(forms.ModelForm):
    delivery_typ = forms.ChoiceField(label=_('Delivery method'), choices=[])

    class Meta:
        model = models.DeliveryGroup
        fields = ('delivery_typ',)

    def __init__(self, *args, **kwargs):
        super(DeliveryMethodForm, self).__init__(*args, **kwargs)
        self.fields['delivery_typ'].choices = handler.get_delivery_types(self.instance)


class BaseDeliveryMethodFormset(BaseModelFormSet):
    def save(self, session):
        data = {}
        for form in self.forms:
            data[form.instance.pk] = form.cleaned_data['delivery_typ']
        session['satchless_delivery_groups'] = data

DeliveryMethodFormset = modelformset_factory(models.DeliveryGroup,
        form=DeliveryMethodForm, formset=BaseDeliveryMethodFormset, extra=0)

def get_delivery_details_forms(order, request):
    forms = []
    for group in order.groups.all():
        Form = handler.get_delivery_formclass(group,
                request.session['satchless_delivery_groups'][group.pk])
        if Form:
            forms.append(Form(data=request.POST or None, prefix='delivery_group-%s' % group.pk))
    return forms
