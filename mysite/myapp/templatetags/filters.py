# All filters are written here
from django import template

register = template.Library() 

@register.filter
def make_positive(value):
    return abs(value)

@register.filter
def add(value,arg):
    return value + arg


