from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Template tag that replaces or adds specific URL parameters while keeping all existing ones.
    
    Usage:
    <a href="?{% url_replace page=1 %}">Page 1</a>
    """
    params = context['request'].GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode() 