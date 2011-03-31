# coding: utf-8

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.template.loader import render_to_string
from django.utils.http import int_to_base36

from accounts.fields import ReCaptchaField
from accounts.tokens import registration_token_generator


class RegistrationForm(forms.Form):
    """
    Registration form
    """
    
    # Required fields from User model
    username = forms.RegexField(label='Username', regex=r'^\w+$', max_length=30, help_text='30 characters or fewer. Letters, numbers and _ character are allowed.')
    first_name = forms.CharField(label='First name', max_length=30)
    last_name = forms.CharField(label='Last name', max_length=30)
    email = forms.EmailField(label='E-mail address', max_length=75, help_text='You will shortly receive an e-mail containing the instructions on how to activate your account at the specified e-mail address.')
    password = forms.CharField(label='Desired password', max_length=128, widget=forms.PasswordInput)
    
    # Optional form fields from UserProfile model
    academic_affiliation = forms.CharField(label='Present academic affiliation', max_length=150, required=False)
    public_email = forms.EmailField(label='Public e-mail address', max_length=75, required=False)
    web_page = forms.URLField(label='Publicly visible web page address', max_length=200, verify_exists=False, required=False)
    notes = forms.CharField(label='Miscellaneous notes', max_length=1500, required=False, widget=forms.Textarea)
    
    # Protection against automatic registration
    captcha = ReCaptchaField('Captcha')
    
    def clean_username(self):
         """
         Validate that the username is not already in use
         """
         
         username = self.cleaned_data['username']
         try:
             User.objects.get(username__iexact=username)
         except User.DoesNotExist:
             return username
         
         raise forms.ValidationError('User with that username already exists.')
    
    def clean_email(self):
        """
        Validate that the email is not already in use
        """
        
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return email
        
        raise forms.ValidationError('This email address is already in use. Please supply a different email address.')

    def save(self, request):
        """
        Create new inactive user, fill up profile and email its activation key to the user.
        """
        
        # Create new inactive user
        user = User.objects.create_user(self.cleaned_data['username'],
                                        self.cleaned_data['email'],
                                        self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False
        user.save()
        
        # Fill up user profile
        profile = user.get_profile()
        profile.academic_affiliation = self.cleaned_data['academic_affiliation']
        profile.public_email = self.cleaned_data['public_email']
        profile.web_page = self.cleaned_data['web_page']
        profile.notes = self.cleaned_data['notes']
        profile.save()
        
        # Email activation key to the user
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        
        context = {
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user.id),
            'user': user,
            'token': registration_token_generator.make_token(user),
            'protocol': 'http',
            'expire': settings.REGISTRATION_TIMEOUT_DAYS,
        }
        
        subject = u'Registration confirmation on %s' % site_name
        message = render_to_string('registration/registration_email.txt', context)
        user.email_user(subject, message)
