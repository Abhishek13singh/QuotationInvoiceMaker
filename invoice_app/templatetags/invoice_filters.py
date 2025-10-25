from django import template

register = template.Library()

@register.filter
def sum_total(items):
    return sum(item.total for item in items)