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

@register.filter
def tax(price):
    try:
        return price.gross - price.net
    except AttributeError:
        return ''

@register.filter
def tax_name(price):
    try:
        return price.tax_name
    except AttributeError:
        return ''
