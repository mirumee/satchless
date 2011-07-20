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


class PaymentProvider(object):
    unique_id = None

    def enum_types(self, order=None, customer=None):
        '''
        Should return an iterable consisting of pairs suitable for a select
        widget. With parameters provided, it should return valid set of
        types matching the given order or customer or their combination.
        '''
        raise NotImplementedError()

    def get_configuration_form(self, order, typ, data):
        '''
        If applicable, return a form responsible for getting any additional
        payment data.
        '''
        return None

    def create_variant(self, order, typ, form):
        '''
        Take a valid form instance if any and create a PaymentVariant instance.
        '''
        raise NotImplementedError()

    def confirm(self, order):
        '''
        Confirm the payment, raise PaymentFailure on errors.
        Backends which need a confirmation form should raise
        ConfirmationFormNeeded.
        '''
        raise NotImplementedError()
