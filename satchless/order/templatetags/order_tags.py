from django.template import Library
from satchless.order import handler

register = Library()

@register.filter
def delivery_type(typ):
    return handler.get_delivery_type_name(typ)

