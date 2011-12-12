import satchless.order.app

from carts.app import cart_app

order_app = satchless.order.app.MagicOrderApp(cart_app=cart_app)
