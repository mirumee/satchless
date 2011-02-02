class PaymentProvider(object):
    def enum_types(self, customer, order=None):
        '''
        Should return an iterable consisting of pairs suitable for a select
        widget.
        '''
        raise NotImplementedError()

    def get_configuration_form(self, customer, order, typ):
        '''
        If applicable, return a form class responsible for getting any
        additional payment data.
        '''
        return None

    def get_variant(self, customer, order, typ, form):
        '''
        Take a valid form instance if any and return a PaymentVariant instance.
        '''
        raise NotImplementedError()

    def get_confirmation_form(self, customer, order, variant):
        '''
        Build a form that can be used on the order confirmation page to start
        payment processing.
        '''
        raise NotImplementedError()
