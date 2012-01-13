# -*- coding: utf-8 -*-
# coding: utf-8

from django.template import Library
from django.template.defaultfilters import stringfilter

from network.network_settings import PARAMS_ORDER

register = Library()

@register.filter()
def label_escape(s, modeltype=None):
    """ escape the label of device """
    l = s.split('_')
    upper_abb = lambda x: len(x)<4 and x.upper() or x.capitalize()
    l = map(upper_abb, l)
    return ' '.join(l)
label_escape.is_safe = True
label_escape = stringfilter(label_escape)

@register.filter()
def itemize(s, label=None):
    """
    converts dictionary to string
    """
    if s:
        if label:
            st = ''
            params = PARAMS_ORDER[str(label)]
            params = params[0] + params[1]
            if params:
                for param in params:
                    if param in s:
                        if ',' in s[param]:
                            if len(s[param]) < 20:
                                st += '%s:%s, ' %(param.replace('_', ' '), s[param])
                            else:
                                st += '%s:%s.., ' %(param.replace('_', ' '), s[param][:20])
                        else:
                            if s[param]:
                                st += '%s:%.2f, ' %(param.replace('_', ' '), float(s[param]))
                st = st[:-2]
                return st   
        l = s.items()
        l.sort()
        l = ["%s: %s" %(str(i[0]),str(i[1])) for i in l]
        return ', '.join(l)
    return None
itemize.is_safe = True
itemize = stringfilter(itemize)

@register.filter()
def index(s, index):
    l = s.split('<!--cut-->')
    return str(l[int(index)])
index.is_safe = True
index = stringfilter(index)