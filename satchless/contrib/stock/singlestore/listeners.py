from django.utils.translation import ugettext

from ....cart.signals import cart_quantity_change_check

def max_stock_level_to_cart(sender, instance=None,
    variant=None, old_quantity=None, new_quantity=None, result=None, **kwargs):
    try:
        stock_level = variant.stock_level
    except AttributeError:
        # not tracked in stock, allow any quantity
        return
    if new_quantity <= stock_level:
        return
    if stock_level == 0:
        reason = ugettext("There is no more %s in stock.") % variant
    else:
        reason = ugettext("You have ordered more %s than we have currently in stock.") % variant
    result.append((stock_level, reason))

def start_listening():
    cart_quantity_change_check.connect(max_stock_level_to_cart)