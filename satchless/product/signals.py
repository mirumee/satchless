from django import dispatch

product_view = dispatch.Signal(providing_args=['instances', 'request', 'response', 'extra_context'])
product_view.__doc__ = """
Launched upon every view of Product or Variant instance(s). May modify
the instances, provide extra context that will go to the template, or
append a HttpResponse object which will be returned instead of the
product page.
"""
