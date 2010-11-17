from django import template

register = template.Library()

@register.filter
def net(price):
    try:
        return price.net
    except AttributeError:
        return ''

@register.filter
def gross(price):
    try:
        return price.gross
    except AttributeError:
        return ''
