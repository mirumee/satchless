from prices import Price

from ...product.tests import product_app
from ...util.models import construct
from .. import models


class TestCart(models.Cart):
    pass


class TestCartItem(construct(models.CartItem, cart=TestCart,
                             variant=product_app.Variant)):
    pass

from .app import AppTestCase
from .magic_app import MagicAppTestCase, cart_app
from .models import ModelsTestCase

__all__ = ['AppTestCase', 'cart_app', 'MagicAppTestCase', 'ModelsTestCase']
