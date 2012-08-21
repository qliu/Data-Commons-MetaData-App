"""=============================================================================
custom_filter.py

Custom filter for Django template
============================================================================="""
from django import template
register = template.Library()

@register.filter(name='replace')
def replace(value,arg):
    str = arg.split(",")
    return value.replace(str[0],str[1])