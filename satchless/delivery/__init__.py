class DeliveryType(object):
    name = None
    provider = None
    typ = None

    def __init__(self, provider, typ, name):
        self.provider = provider
        self.typ = typ
        self.name = name

    def __repr__(self):
        return '<DeliveryType(provider=%s, typ=%s, name=%s)>' % (repr(self.provider),
                                                                 repr(self.typ),
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
                for t in self.enum_types(delivery_group=delivery_group,
                                         customer=customer)]

    def get_configuration_form(self, delivery_group, data, typ=None):
        '''
        If applicable, return a form responsible for getting any additional
        delivery data.
        '''
        return None

    def get_configuration_forms_for_groups(self, delivery_groups, data):
        delivery_group_forms = []
        delivery_types = dict((dt.typ, dt) for dt in self.enum_types())
        for group in delivery_groups:
            form = self.get_configuration_form(group, data)
            delivery_group_forms.append((group, delivery_types[group.delivery_type], form))
        return delivery_group_forms

    def save(self, delivery_group, form):
        '''
        Take a valid form instance if any and creates a DeliveryVariant instance.
        '''
        raise NotImplementedError()