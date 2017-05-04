from django.template import Library

register = Library()


@register.simple_tag
def value(value):
    """
    Return value unless it's None in which case we return 'No Value Set'
    """
    if value is None or value == '':
        return '-'
    else:
        return value
