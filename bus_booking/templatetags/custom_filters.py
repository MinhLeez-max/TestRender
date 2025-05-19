from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    if value:
        return value.split(delimiter)
    return []
@register.filter
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value
