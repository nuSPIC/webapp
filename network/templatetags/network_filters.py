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
            params = PARAMS_ORDER.get(str(label))

            if params:
                params = params[0] + params[1]
                for param in params[1:]:
                    if param in s and not param in ['label', 'model', 'type']:
                        if ',' in str(s[param]):
                            if len(s[param]) < 20:
                                st += '%s: %s, ' %(param, s[param])
                            else:
                                st += '%s: %s.., ' %(param, s[param][:20])
                        else:
                            if str(s[param]).isdigit():
                                st += '%s: %d, ' %(param, int(s[param]))
                            else:
                                try:
                                    st += '%s: %.2f, ' %(param, float(s[param]))
                                except:
                                    st += '%s: %s, ' %(param, s[param])
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

@register.filter()
def modeltype(model):
        # get modeltype of device.
    if 'generator' in model:
        return 'input'
    elif 'meter' in model or 'detector' in model:
        return 'output'
    else:
        return 'neuron'

@register.filter()
def truncate_float(s, max_len):
    try:
        f = float(s)
        return str(int(f)) + str(abs(f%1.))[1:int(max_len)+1]
    except:
        return s

@register.filter
def count(obj, user_id):
    return obj.count(user_id)
