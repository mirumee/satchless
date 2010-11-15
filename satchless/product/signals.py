from django import dispatch
# XXX: do not import models, they import us

product_view = dispatch.Signal(providing_args=['instances', 'request', 'response', 'extra_context'])
product_view.__doc__ = """
Launched upon every view of Product or Variant instance(s). May modify
the instances, provide extra context that will go to the template, or
append a HttpResponse object which will be returned instead of the
product page.
"""

variant_formclass_for_product = dispatch.Signal(providing_args=['instance', 'formclass'])
variant_formclass_for_product.__doc__ = """
Finds variant selection form clas for given product instance and appends
it to the form list.
"""

product_unit_price_range_query = dispatch.Signal(providing_args=['instance'])
product_unit_price_range_query.__doc__ = """
Checks for product price at quantity of 1. Listeners should set
`instance.unit_price_range` field.
"""

variant_unit_price_query = dispatch.Signal(providing_args=['instance', 'quantity'])
variant_unit_price_query.__doc__ = """
Checks for variant unit price at given quantity. Listeners should set
`instance.unit_price` field.
"""
