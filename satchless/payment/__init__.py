class PaymentFailure(Exception):
    def __init__(self, error_message):
        super(PaymentFailure, self).__init__(error_message)
        self.error_message = error_message


class ConfirmationFormNeeded(Exception):
    def __init__(self, form=None, action='', method='post'):
        super(ConfirmationFormNeeded, self).__init__()
        self.form = form
        self.action = action
        self.method = method


class PaymentType(object):
    typ = None
    name = None

    def __init__(self, typ, name):
        self.typ = typ
        self.name = name

    def __repr__(self):
        return '<PaymentType(typ=%s, name=%s)>' % (repr(self.typ),
                                                   repr(self.name))


class PaymentProvider(object):
    def enum_types(self, order=None, customer=None):
        '''
        Should return an iterable consisting of pairs suitable for a select
        widget. With parameters provided, it should return valid set of
        types matching the given order or customer or their combination.
        '''
        raise NotImplementedError()

    def as_choices(self, order=None, customer=None):
        return [(t.typ, t.name)
                for p, t in self.enum_types(order=order,
                                            customer=customer)]

    def get_configuration_form(self, order, data, typ=None):
        '''
        If applicable, return a form responsible for getting any additional
        payment data.
        '''
        return None

    def create_variant(self, order, form, typ=None):
        '''
        Take a valid form instance if any and create a PaymentVariant instance.
        '''
        raise NotImplementedError()

    def confirm(self, order, typ=None):
        '''
        Confirm the payment, raise PaymentFailure on errors.
        Backends which need a confirmation form should raise
        ConfirmationFormNeeded.
        '''
        raise NotImplementedError()
