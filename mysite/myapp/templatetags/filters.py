# All filters are written here
from django import template

DISPLAY_FORMAT = 5

register = template.Library() 

@register.filter
def make_positive(value):
    return abs(value)

@register.filter
def add(value,arg):
    return value + arg

@register.filter
def length(value):
    return len(value)

@register.filter
def display_name(value):
    if type(value) is not str:
        value = str(value)
    temp = list(value)
    t_len = len(temp)

    if t_len > DISPLAY_FORMAT:
        value = value[0:5] + '...'

    return value


