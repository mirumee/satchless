from satchless.cart import app

class WishlistApp(app.CartApp):
    app_name = 'wishlist'
    cart_type = 'wishlist'

class CartApp(app.CartApp):
    app_name = 'cart'
    cart_type = 'cart'

	
wishlist_app = WishlistApp()
cart_app = CartApp()
