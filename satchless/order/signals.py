# -*- coding: utf-8 -*-
from django import dispatch
# ☠ do not import models here. they import us. ☠

order_status_changed = dispatch.Signal(providing_args=['old_status'])
order_status_changed.__doc___ = """
Sent whenever order status is changed.
"""

order_pre_confirm = dispatch.Signal(providing_args=['request'])
order_pre_confirm.__doc__ = """
Sent just before we attempt to confirm the order.
The confirmation may require user interaction or not. This signal is being
sent in the last moment of being under control of satchless.
"""
