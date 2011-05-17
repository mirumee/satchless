from django.template import Library
from satchless.order import handler

register = Library()

@register.filter
def delivery_type(typ):
    provider, short_typ = handler.get_delivery_provider(typ)
    return provider.get_type_instance(short_typ)

