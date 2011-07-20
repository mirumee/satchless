class DeliveryProvider(object):
    unique_id = None

    def enum_types(self, customer=None, delivery_group=None):
        '''
        Should return an iterable consisting of pairs suitable for a select
        widget. When given a DeliveryGroup it should only return types
        available for that group.
        '''
        raise NotImplementedError()

    def get_configuration_form(self, delivery_group, typ, data):
        '''
        If applicable, return a form responsible for getting any additional
        delivery data.
        '''
        return None

    def create_variant(self, delivery_group, typ, form):
        '''
        Take a valid form instance if any and creates a DeliveryVariant instance.
        '''
        raise NotImplementedError()
