# -*- coding: utf-8 -*-
# coding: utf-8

from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter()
def readable(s):
    """
    labels a string 
    """
    l = s.split('_')
    upper_abb = lambda x: len(x)<4 and x.upper() or x.capitalize()
    l = map(upper_abb, l)
    return ' '.join(l)
readable.is_safe = True
readable = stringfilter(readable)

@register.filter()
def label_escape(s, modeltype=None):
    """ escape the label of device """
    if modeltype == 'neuron':
        return 'Neuron'
    else:
        l = s.split('_')
        upper_abb = lambda x: len(x)<4 and x.upper() or x.capitalize()
        l = map(upper_abb, l)
        return ' '.join(l)
readable.is_safe = True
readable = stringfilter(readable)

@register.filter()
def itemize(s):
    """
    converts dictionary to string
    """
    if s:
        l = s.items()
        l.sort()
        l = ["%s: %s" %(str(i[0]),str(i[1])) for i in l]
        return ', '.join(l)
    return None
itemize.is_safe = True
itemize = stringfilter(itemize)

@register.filter()
def split(s, index):
    l = s.split('<!--cut-->')
    return str(l[int(index)])
split.is_safe = True
split = stringfilter(split)