from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """Returns True if value ends with arg."""
    try:
        return value.lower().endswith(arg.lower())
    except (AttributeError, TypeError):
        return False
