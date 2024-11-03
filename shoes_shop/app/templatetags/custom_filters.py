from django import template

register = template.Library()

@register.filter
def currency(value):
    return "{:,.0f} VND".format(value)
