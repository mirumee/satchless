# -*- coding: utf-8 -*-
from django import dispatch
# ☠ do not import models here. they import us. ☠

cart_quantity_change_check = dispatch.Signal(providing_args=['variant', 'old_qty', 'new_qty', 'result'])
cart_quantity_change_check.__doc___ = """
Sent to check if it is possible to change item's quantity to new value.
It passes old and new quantity as arguments and may receive a result as tuple
``(result_quantity, reason)`` where reason is a message to be shown to the
user."""

cart_content_changed = dispatch.Signal()
cart_content_changed.__doc__ = """
Sent whenever cart's content has been changed.
"""

cart_item_added = dispatch.Signal()
cart_item_added.__doc__ = """
Sent whenever new item is added to the cart.
"""

cart_item_removed = dispatch.Signal()
cart_item_removed.__doc__ = """
Sent whenever item is removed from the cart.
"""
