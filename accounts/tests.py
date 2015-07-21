from django.test import TestCase
from accounts.models import User,UserProfile

username = 'username'
first_name = 'Max'
last_name = 'Mustermann'
email = 'foo@example.com'
password = 'password'
ip_address = '127.0.0.1'

class UserTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username=username,
            first_name=first_name, last_name=last_name,
            email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

    def test_get_full_name(self):
        """Animals that can speak are correctly identified"""
        user = User.objects.get(username=username)
        self.assertEqual(user.get_full_name(), '%s %s' %(first_name, last_name))

    def test_has_email(self):
        """Animals that can speak are correctly identified"""
        user = User.objects.get(username=username)
        self.assertEqual(user.email, email)

    def test_has_password(self):
        """Animals that can speak are correctly identified"""
        user = User.objects.get(username=username)
        self.assertNotEqual(user.password, password)

    def test_is_inactive(self):
        user = User.objects.get(username=username)
        self.assertFalse(user.is_active)

class UserProfileTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username=username)
        profile = UserProfile.objects.create(user=user)
        profile.ip_address = ip_address
        profile.save()

    def test_username_title(self):
        profile = User.objects.get(username=username).profile
        self.assertEqual(str(profile), username)

    def test_has_ip_adress(self):
        profile = User.objects.get(username=username).profile
        self.assertEqual(profile.ip_address, ip_address)

    def test_get_absolute_url(self):
        profile = User.objects.get(username=username).profile
        self.assertEqual(profile.get_absolute_url(), '/accounts/%s/' %profile.user.id)
