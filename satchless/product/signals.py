from django import dispatch

product_view = dispatch.Signal(providing_args=['request', 'product', 'extra_context', 'response'])
product_view.__doc__ = """Launched upon every view of a product. May modify extra context that
will go to the template, or append a HttpResponse object which will be returned instead of the
product page."""
