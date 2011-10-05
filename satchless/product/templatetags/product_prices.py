from django.conf import settings
from django import template
from django.template.base import Node
from django.template.defaulttags import kwarg_re
from django.utils.encoding import smart_str

register = template.Library()

class BasePriceNode(Node):
    def __init__(self, item, kwargs, asvar):
        self.item = item
        self.kwargs = kwargs
        self.asvar = asvar

    def get_price(self, item, currency, **kwargs):
        raise NotImplementedError

    def get_currency_for_item(self, item):
        return getattr(settings, 'SATCHLESS_DEFAULT_CURRENCY', None)

    def render(self, context):
        from satchless.pricing.handler import pricing_queue
        item = self.item.resolve(context)
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        self.pricing_handler = kwargs.pop('handler', pricing_queue)
        currency = kwargs.pop('currency', self.get_currency_for_item(item))
        result = ''
        if currency:
            r = self.get_price(item, currency, **kwargs)
            if r:
                result = r

        if self.asvar:
            context[self.asvar] = result
            return ''
        return result

class VariantPriceNode(BasePriceNode):
    def get_price(self, product, currency, **kwargs):
        return self.pricing_handler.get_variant_price(product, currency, **kwargs)

class ProductPriceRangeNode(BasePriceNode):
    def get_price(self, product, currency, **kwargs):
        return self.pricing_handler.get_product_price_range(product, currency, **kwargs)

def parse_price_tag(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
                "'%s' syntax is {%% %s <instance> [currency='<iso-code>'] as <variable-name> %%}" % (
                    bits[0], bits[0]))
    product = parser.compile_filter(bits[1])
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise template.TemplateSyntaxError("Malformed arguments to '%s' tag" % bits[0])
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                raise template.TemplateSyntaxError("'%s' takes only named arguments" % bits[0])
    return product, kwargs, asvar

@register.tag
def variant_price(parser, token):
    return VariantPriceNode(*parse_price_tag(parser, token))

@register.tag
def product_price_range(parser, token):
    return ProductPriceRangeNode(*parse_price_tag(parser, token))
