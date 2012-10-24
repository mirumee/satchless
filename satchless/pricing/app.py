from django.conf import settings
from .handler import PricingQueue


class ProductAppPricingMixin(object):

    def __init__(self, *args, **kwargs):
        self.pricing_handler = kwargs.pop(
            'pricing_handler', PricingQueue(*getattr(settings,
                                                     'SATCHLESS_PRICING_HANDLERS', ())))
        super(ProductAppPricingMixin, self).__init__(*args, **kwargs)

    def get_context_data(self, *args, **context):
        return super(ProductAppPricingMixin, self).get_context_data(
            *args, pricing_handler=self.pricing_handler, **context)

