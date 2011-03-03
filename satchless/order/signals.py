# -*- coding: utf-8 -*-
from django import dispatch
# ☠ do not import models here. they import us. ☠

order_status_changed = dispatch.Signal(providing_args=['old_status'])
order_status_changed.__doc___ = """
Sent whenever order status is changed.
"""
