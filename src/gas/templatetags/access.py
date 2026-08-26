from django import template

register = template.Library()


@register.filter
def access(value, arg):
    """
    Dict access by variable
    Use `{{ some_dict|access:var }}`
    """

    try:
        output = value[arg]
    except (KeyError, TypeError):
        output = getattr(value, arg, None)

    return output
