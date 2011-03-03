class PaymentProvider(object):
    def enum_types(self, order=None, customer=None):
        '''
        Should return an iterable consisting of pairs suitable for a select
        widget. With parameters provided, it should return valid set of
        types matching the given order or customer or their combination.
        '''
        raise NotImplementedError()

    def get_configuration_formclass(self, order, typ):
        '''
        If applicable, return a form class responsible for getting any
        additional payment data.
        '''
        return None

    def get_variant(self, order, typ, form):
        '''
        Take a valid form instance if any and return a PaymentVariant instance.
        '''
        raise NotImplementedError()

    def get_confirmation_form(self, order):
        '''
        Build a form that can be used on the order confirmation page to start
        payment processing.
        '''
        raise NotImplementedError()
