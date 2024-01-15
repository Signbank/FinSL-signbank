from django.template import Library

register = Library()


@register.simple_tag
def url_parameter_extend(request, **kwargs):
    """
    A template tag that appends new parameters to the QueryDict.
    """
    extended = request.GET.copy()
    extended.update(kwargs)
    return extended.urlencode()