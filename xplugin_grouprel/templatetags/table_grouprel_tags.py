from django import template
import json

register = template.Library()


@register.filter
def json_dumps(data):
    """Removes all values of arg from the given string"""
    return json.dumps(data)
