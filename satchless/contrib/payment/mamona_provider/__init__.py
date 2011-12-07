from mamona.utils import get_backend_choices

from ....payment import (PaymentProvider, ConfirmationFormNeeded,
                               PaymentType)
from . import models
from . import listeners

class MamonaProvider(PaymentProvider):
    def enum_types(self, order=None, customer=None):
        for typ, name in get_backend_choices():
            yield self, PaymentType(typ=typ, name=name)

    def create_variant(self, order, typ, form):
        variant = models.MamonaPaymentVariant.objects.get_or_create(order=order,
                                                                    name=typ.name,
                                                                    price=0)[0]
        models.Payment.objects.create(order=variant, amount=order.total().gross,
                                      currency=order.currency, backend=typ)
        return variant

    def confirm(self, order, typ):
        payment = order.paymentvariant.get_subtype_instance().payments.get()
        form = payment.get_processor().get_confirmation_form(payment)
        raise ConfirmationFormNeeded(**form)

provider = MamonaProvider()

listeners.start_listening()
