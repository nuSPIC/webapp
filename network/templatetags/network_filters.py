# coding: utf-8

from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter()
def truncate(s, max_len):
    """
    Truncates a string after a certain number of letters
    """
    
    try:
        length = int(max_len)
    except ValueError:
        return s
    
    if len(s) > length:
        return s[:length] + '...'
    else:
        return s[:length] 
truncate.is_safe = True
truncate = stringfilter(truncate)

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