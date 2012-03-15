import authorizenet
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ....util.models import DeferredOneToOneField

class AuthorizeNetPaymentBase(models.Model):
    cc_name = models.CharField(_('Name on Credit Card'), max_length=128)
    cc_number = models.CharField(_('Card Number'), max_length=32)
    cc_expiration = models.DateField(_('Exp. date'), null=True)
    cc_cvv2 = models.CharField(_('CVV2 Security Number'), max_length=4)
    response = models.ForeignKey(authorizenet.models.Response, null=True,
                                 blank=True, editable=False)
    order = DeferredOneToOneField('order', related_name='payment', editable=False)

    class Meta:
        abstract = True

    def cc_number_starred(self):
        value = '%s%s' % ((len(self.cc_number) - 4) * u'\u25cf', self.cc_number[-4:])
        value = ' '.join([value[i:i+4] for i in range(0, len(value), 4)])
        return value
    cc_number_starred.short_description = _('Card number')
