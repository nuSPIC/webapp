# -*- coding: utf-8 -*-
# coding: utf-8

from django.template import Library
from django.template.defaultfilters import stringfilter
from math import ceil


register = Library()

@register.filter
def columns(thelist, n):
    """
    Split a list into `n` columns
    """
    
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    
    list_len = len(thelist)
    split = float(list_len) / n
    
    return [thelist[int(ceil(i * split)):int(ceil((i + 1) * split))]
            for i in xrange(n)]
            
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
