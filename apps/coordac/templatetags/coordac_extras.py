# apps/coordac/templatetags/coordac_extras.py
from django import template

register = template.Library()

@register.filter(name="dict_get")
def dict_get(value, key):
    """
    value: diccionario (por ejemplo 'existing')
    key: llave (por ejemplo tutor.id)
    """
    if isinstance(value, dict):
        return value.get(key)
    return None
