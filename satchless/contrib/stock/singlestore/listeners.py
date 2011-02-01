from django.utils.translation import ugettext as _
from satchless.cart.signals import cart_quantity_change_check
from .models import StockLevel

def max_stock_level_to_cart(sender, instance=None,
    variant=None, old_quantity=None, new_quantity=None, result=None, **kwargs):
    try:
        level = variant.stocklevel
    except StockLevel.DoesNotExist:
        # not tracked in stock, allow any quantity
        return
    if new_quantity <= level.quantity:
        return
    if level.quantity == 0:
        reason = _("There is no more %s in stock.") % variant
    else:
        reason = _("You have ordered more %s than we have currently in stock.") % variant
    result.append((level.quantity, reason))

cart_quantity_change_check.connect(max_stock_level_to_cart)
