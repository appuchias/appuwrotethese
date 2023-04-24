from django import template

register = template.Library()


@register.filter
def relevel(level):
    """
    Level replacing filter
    Use `{{ message.level_tag|relevel }}`
    """
    levels = {
        "debug": "primary",
        "info": "secondary",
        "success": "success",
        "warning": "warning",
        "error": "danger",
    }
    return levels.get(level, "dark")
