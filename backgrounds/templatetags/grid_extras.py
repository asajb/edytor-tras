from django import template

register = template.Library()

@register.filter
def make_range(value):
    """Returns a range from 0 to the given value."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return []
    

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)