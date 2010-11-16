from django import dispatch
# XXX: do not import models, they import us

cartitem_unit_price_query = dispatch.Signal(providing_args=['instance', 'price'])
cartitem_unit_price_query.__doc__ = """
Checks for variant unit price within given cart.
"""
