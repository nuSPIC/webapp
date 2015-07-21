from django.test import TestCase


class PackagesTestCase(TestCase):

    def test_version_celery(self):
        import celery
        self.assertEqual(celery.__version__, '2.3.3')

    def test_version_django(self):
        import django
        self.assertEqual(django.__version__, '1.3.1')
