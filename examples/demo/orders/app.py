from satchless.order.app import OrderApp
from models import DemoOrder

class DemoOrderApp(OrderApp):

    order_model = DemoOrder

order_app = DemoOrderApp()