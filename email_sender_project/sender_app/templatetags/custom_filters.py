from django import template

register = template.Library()

@register.filter
def times(value, arg):
    return value * arg
