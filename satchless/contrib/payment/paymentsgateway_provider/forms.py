from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import models

class PaymentForm(forms.ModelForm):
    pg_client_token = forms.CharField(max_length=50, required=False,
                                      label=_('PaymentsGateway Client Token'))
    pg_payment_token = forms.CharField(max_length=50, required=False,
                                       label=_('PaymentsGateway Payment Method Token'))

    class Meta:
        model = models.PaymentsGatewayVariant
        fields = ('amount', 'pg_client_token', 'pg_payment_token',
                  'description')

    def clean(self):
        if not self.cleaned_data.get('pg_client_token') \
           and not self.cleaned_data.get('pg_payment_token'):
            raise ValidationError(_("Either a Payment Method or Client is required"))
        return super(PaymentForm, self).clean()

class PaymentsGatewayReceiptForm(forms.ModelForm):
    class Meta:
        model = models.PaymentsGatewayReceipt

