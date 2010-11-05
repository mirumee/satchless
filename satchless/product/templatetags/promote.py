from django import template
from django.db import models

register = template.Library()

class PromoteNode(template.Node):
    def __init__(self, arg, var_name):
        self.arg = template.Variable(arg)
        self.var_name = var_name

    def render(self, context):
        obj = self.arg.resolve(context)
        if isinstance(obj, models.Model):
            context[self.var_name] = obj.get_subtype_instance()
        else:
            context[self.var_name] = [o.get_subtype_instance() for o in obj]
        return ''

@register.tag(name='promote')
def do_promote(parser, token):
    class PromoteParser(template.TokenParser):
        def top(self):
            arg = self.value()
            assert self.tag() == 'as'
            var_name = self.tag()
            return (arg, var_name)

    arg, var_name = PromoteParser(token.contents).top()
    return PromoteNode(arg, var_name)
