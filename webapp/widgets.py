from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

class CustomRadioFieldRenderer(widgets.RadioFieldRenderer):
    def render(self):
        return mark_safe(u'<ul>\n%s\n</ul>' % u'\n'.join([u'<li class="radio">%s</li>'
            % force_unicode(w) for w in self]))

class CustomRadioSelect(widgets.RadioSelect):
    renderer = CustomRadioFieldRenderer
