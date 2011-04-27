# coding: utf-8

from django.template import Library
import re


register = Library()

@register.filter
def highlight(s, term):
    """
    Highlights the search string around HTML tags
    """
    
    return re.sub(r'(?i)([^<]*)(%s)([^>]*)' % term, r'\1<span class="highlight">\2</span>\3', s)
