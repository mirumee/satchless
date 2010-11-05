from django import dispatch

product_view = dispatch.Signal(providing_args=['request', 'extra_context', 'response'])
product_view.__doc__ = """
Launched upon every view of a product instance. May modify extra context
that will go to the template, or append a HttpResponse object which will
be returned instead of the product page.
"""

variant_formclass_for_product = dispatch.Signal(providing_args=['formclass'])
variant_formclass_for_product.__doc__ = """
Finds variant selection form clas for given product instance and appends
it to the form list.
"""
