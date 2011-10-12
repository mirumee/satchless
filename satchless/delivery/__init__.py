class DeliveryType(object):
    typ = None
    name = None

    def __init__(self, typ, name):
        self.typ = typ
        self.name = name

    def __repr__(self):
        return '<DeliveryType(typ=%s, name=%s)>' % (repr(self.typ),
                                                    repr(self.name))


class DeliveryProvider(object):
    def enum_types(self, delivery_group=None, customer=None):
        '''
        Should return an iterable consisting of pairs suitable for a select
        widget. When given a DeliveryGroup it should only return types
        available for that group.
        '''
        raise NotImplementedError()

    def as_choices(self, delivery_group=None, customer=None):
        return [(t.typ, t.name)
                for p, t in self.enum_types(delivery_group=delivery_group,
                                            customer=customer)]

    def get_configuration_form(self, delivery_group, data):
        '''
        If applicable, return a form responsible for getting any additional
        delivery data.
        '''
        return None

    def create_variant(self, delivery_group, form):
        '''
        Take a valid form instance if any and creates a DeliveryVariant instance.
        '''
        raise NotImplementedError()