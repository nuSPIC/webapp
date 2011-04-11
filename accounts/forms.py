# coding: utf-8

from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils.timesince import timeuntil

from accounts.fields import ReCaptchaField
from accounts.models import UserProfile

from datetime import datetime


class UserEditForm(forms.ModelForm):
    """
    User edit form
    
    Used on the "Edit profile" page
    """
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)


class UserRegistrationForm(forms.ModelForm):
    """
    User registration form
    """
    
    username = forms.RegexField(regex=r'^\w+$', help_text='30 characters or fewer. Letters, numbers and _ character are allowed.')
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True, help_text='You will shortly receive an e-mail containing the instructions on how to activate your account at the specified e-mail address.')
    password = forms.CharField(widget=forms.PasswordInput, help_text='')
    
    # Protection against automatic registration
    captcha = ReCaptchaField(label='')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)

    def clean_email(self):
        """
        Check that the email is not already in use
        """
        
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return email
        
        raise forms.ValidationError('This email address is already in use. Please supply a different email address.')


class ProfileEditForm(forms.ModelForm):
    """
    User profile edit form
    
    Used on the registration and edit profile pages
    """
    
    class Meta:
        model = UserProfile
        fields = ('academic_affiliation', 'public_email', 'web_page', 'notes',)
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)
        

class CustomPasswordResetForm(PasswordResetForm):
    """
    Checks what is the period of time between two e-mail requests and
    and doesn't allow to send email if it is less than EMAIL_REQUEST_DELAY
    """
    
    def as_div(self):
        return self._html_output(u'<div class="field-wrapper">%(label)s %(errors)s %(field)s%(help_text)s</div>', u'%s', '</div>', u'<span class="help_text">%s</span>', False)
    
    def clean_email(self):
        email = super(CustomPasswordResetForm, self).clean_email()
        
        now = datetime.today()
        for user in self.users_cache:
            profile = user.get_profile()
            if profile.last_email_request and ((now - profile.last_email_request) < settings.EMAIL_REQUEST_DELAY):
                d = profile.last_email_request + settings.EMAIL_REQUEST_DELAY
                raise forms.ValidationError(
                    'You need to wait %s, before submitting another password reset request. '
                    'If the e-mail with the instructions wouldn\'t come within this period of time, '
                    'be sure to check the spam folder in your e-mail client and please try again.' % timeuntil(d)
                )
        
        return email
    
    def save(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).save(*args, **kwargs)
        
        # Save last password reset request time
        for user in self.users_cache:
            profile = user.get_profile()
            profile.last_email_request = datetime.today()
            profile.save()

            
class AccountSearchForm(forms.Form):
    """
    Account search form
    
    Used on the community page
    """
    
    term = forms.RegexField(label='', regex=r'\w+', required=False)
