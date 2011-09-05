# coding: utf-8

from django.template import Library

register = Library()

@register.simple_tag
def form_field(form, field, context, tag):
    """
        Usage: form_field form field context 'tag'
    """ 
    context[tag] = form.__getitem__(field)
    return ''

@register.filter(name='field_value')
def field_value(field):
    """
        Returns the value of a form field
    """
    try:
        value = field.form.initial[field.name]
        if not value:
            return ''
        return value
    except:
        return ''
