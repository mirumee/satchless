# -*- coding: utf-8 -*-
from django import dispatch
# ☠ do not import models here. they import us. ☠

pre_cart_quantity_change = dispatch.Signal(
        providing_args=['variant', 'old_quantity', 'new_quantity', 'result'])
pre_cart_quantity_change.__doc___ = """
Sent before quantity of a variant is changed in the cart. It passes old and
new quantity as arguments and may receive a result in the following format:
``(result_quantity, reason)`` where reason is a message to be shown to the
user."""
