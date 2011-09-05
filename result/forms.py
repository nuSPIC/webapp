from django import forms
from models import Result

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Result
        fields = ('comment',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)