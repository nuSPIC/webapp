# coding: utf-8

from django.template import Library
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
