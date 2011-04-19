# coding: utf-8

from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.http import base36_to_int, int_to_base36
from django.views.decorators.csrf import csrf_exempt

from accounts.forms import AccountSearchForm, ProfileEditForm, UserEditForm, UserRegistrationForm
from accounts.models import UserProfile
from accounts.tokens import TokenGenerator
from lib.decorators import render_to
from lib.helpers import paginate


@render_to('registration/registration_form.html')
def registration(request):
    """
    Register new user and send email with activation link
    """
    
    if request.POST:
        user_form = UserRegistrationForm(request.POST, prefix='user_form')
        profile_form = ProfileEditForm(request.POST, prefix='profile_form')
        if user_form.is_valid() and profile_form.is_valid():
            # Create new inactive user
            user = user_form.save()
            user.set_password(user_form.cleaned_data['password'])
            user.is_active = False
            user.save()
            
            # Fill user profile with data from registration form
            profile = user.get_profile()
            profile_form = ProfileEditForm(request.POST, instance=profile, prefix='profile_form')
            profile_form.save()
            
            # Send email with activation key to the user
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            registration_token_generator = TokenGenerator(settings.REGISTRATION_TIMEOUT_DAYS)
            
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
            
            return HttpResponseRedirect(reverse('registration_done'))
    else:
        user_form = UserRegistrationForm(prefix='user_form')
        profile_form = ProfileEditForm(prefix='profile_form')
    
    return {
        'user_form': user_form,
        'profile_form': profile_form,
    }


def registration_confirm(request, uidb36, token):
    """
    Check the hash in a link the user clicked and activate account
    """
    
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None
    
    registration_token_generator = TokenGenerator(settings.REGISTRATION_TIMEOUT_DAYS)
    if (user is not None) and registration_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponseRedirect(reverse('registration_complete'))
    else:
        return HttpResponseRedirect(reverse('registration_failed'))


@csrf_exempt
@render_to('community/accounts.html')
def accounts(request, sort_order):
    """
    Shows registered user list, which can be searched and sorted according to several criteria
    """
    
    profiles = UserProfile.objects.exclude(user__is_active=False).select_related('user')
    if isinstance(sort_order, (list, tuple)):
        profiles = profiles.order_by(*sort_order)
    else:
        profiles = profiles.order_by(sort_order)
    
    # Filter user account list with search term
    search_term = ''
    if request.GET:
        search_form = AccountSearchForm(request.GET)
        if search_form.is_valid():
            term = search_form.cleaned_data['term']
            if term:
                profiles = profiles.filter(Q(user__first_name__icontains=term) |
                                           Q(user__last_name__icontains=term))
                search_term = u'term=%s' % term
    else:
        search_form = AccountSearchForm()
    
    page = paginate(request, profiles, settings.ACCOUNTS_PER_PAGE)
    
    return {
        'page': page,
        'search_form': search_form,
        'search_term': search_term,
    }


@render_to('profile/profile.html')
def profile(request, profile_id):
    """
    User profile page
    """
    
    profile = get_object_or_404(UserProfile, id=profile_id)
    
    return {
        'profile': profile
    }


@login_required
@render_to('profile/edit.html')
def profile_edit(request, profile_id):
    """
    Profile edit
    """
    
    profile = get_object_or_404(UserProfile, id=profile_id)
    old_email = profile.user.email
    
    # Allow user edit only his profile
    if profile.user != request.user:
        raise Http404
    
    if request.POST:
        user_form = UserEditForm(request.POST, instance=profile.user, prefix='user_form')
        profile_form = ProfileEditForm(request.POST, instance=profile, prefix='profile_form')
        
        if user_form.is_valid() and profile_form.is_valid():
            if 'email' in user_form.changed_data:
                # If the user has changed his primary e-mail address,
                # save the new one in the temporary field and send an e-mail
                # with the confirmation link to the new address
                new_email = user_form.cleaned_data['email']
                
                user = user_form.save(commit=False)
                user.email = old_email
                user.save()
                
                # Save new email address in temporary field
                profile = profile_form.save()
                profile.temporary_email = new_email
                profile.save()
                
                # Send the email with the confirmation link to the user
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                email_change_token_generator = TokenGenerator(settings.EMAIL_CHANGE_TIMEOUT_DAYS)
                
                context = {
                    'domain': domain,
                    'site_name': site_name,
                    'uid': int_to_base36(user.id),
                    'user': user,
                    'token': email_change_token_generator.make_token(user),
                    'protocol': 'http',
                    'expire': settings.EMAIL_CHANGE_TIMEOUT_DAYS,
                }
                
                subject = u'Primary e-mail address change confirmation on %s' % site_name
                message = render_to_string('email_change/email_change_email.txt', context)
                user.email_user(subject, message)
                
                return HttpResponseRedirect(reverse('email_change_done'))
            else:
                user_form.save()
                profile_form.save()
                
                return HttpResponseRedirect(reverse('profile', kwargs={'profile_id': profile.id}))
    else:
        user_form = UserEditForm(instance=profile.user, prefix='user_form')
        profile_form = ProfileEditForm(instance=profile, prefix='profile_form')
    
    return {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    }


def email_change_confirm(request, uidb36, token):
    """
    Change the primary email in the case if the hash
    in the link the user clicked was correct
    """
    
    email_change_token_generator = TokenGenerator(settings.EMAIL_CHANGE_TIMEOUT_DAYS)
    
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None
    
    if (user is not None) and email_change_token_generator.check_token(user, token):
        profile = user.get_profile()
        user.email = profile.temporary_email
        user.save()
        
        return HttpResponseRedirect(reverse('email_change_complete'))
    else:
        return HttpResponseRedirect(reverse('email_change_failed'))
