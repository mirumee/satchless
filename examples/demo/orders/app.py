from satchless.order import app
from models import DemoOrder

class OrderApp(app.OrderApp):

    order_model = DemoOrder

order_app = OrderApp()
