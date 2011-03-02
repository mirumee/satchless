from django import forms
from django.core.exceptions import ObjectDoesNotExist
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
    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super(BaseDeliveryMethodFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            if form.instance and form.instance.pk:
                try:
                    form.fields['delivery_typ'].initial = \
                        self.session['satchless_delivery_groups'][form.instance.pk]
                except KeyError:
                    pass

    def save(self, *args, **kwargs):
        session = kwargs.pop('session')
        super(BaseDeliveryMethodFormset, self).save(*args, **kwargs)
        data = {}
        for form in self.forms:
            data[form.instance.pk] = form.cleaned_data['delivery_typ']
        session['satchless_delivery_groups'] = data

DeliveryMethodFormset = modelformset_factory(models.DeliveryGroup,
        form=DeliveryMethodForm, formset=BaseDeliveryMethodFormset, extra=0)

def get_delivery_details_forms_for_groups(order, request):
    '''
    For each delivery group creates a (group, typ, delivery details form) tuple.
    If there is no form, the third element is None.
    '''
    groups_and_forms = []
    for group in order.groups.all():
        typ = request.session['satchless_delivery_groups'][group.pk]
        form = None
        Form = handler.get_delivery_formclass(group, typ)
        if Form:
            try:
                variant = group.deliveryvariant.get_subtype_instance()
            except ObjectDoesNotExist:
                variant = None
            form = Form(data=request.POST or None,
                    instance=variant,
                    prefix='delivery_group-%s' % group.pk)
        groups_and_forms.append((group, typ, form))
    return groups_and_forms


class PaymentMethodForm(forms.ModelForm):
    payment_typ = forms.ChoiceField(label=_('Payment method'), choices=[])

    class Meta:
        model = models.Order
        fields = ('payment_typ',)

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        self.fields['payment_typ'].choices = handler.get_payment_types(self.instance)

    def save(self, session):
        session['satchless_payment_method'] = self.cleaned_data['payment_typ']


def get_payment_details_form(order, request):
    typ = request.session['satchless_payment_method']
    Form = handler.get_payment_formclass(order, typ)
    if Form:
        return Form(data=request.POST or None)
    return None
