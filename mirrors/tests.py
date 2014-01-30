import json
import hashlib

from django.test import TestCase
from django.core.urlresolvers import resolve, reverse
from django.test import Client

from mirrors import urls as content_url
from mirrors.models import Content, ContentRevision

class MirrorsTestCase(TestCase):
    """This class adds the `assertRecursiveDictContains` function, which
    provides a simpler way to make sure one dictionary contains (at least) all
    of the data in another dictionary.
    """

    def assertRecursiveDictContains(self, expected, actual):
        """Assert that one dictionary contains all of the data from another,
        recursive into sub-dictionaries, if necessary.  

        :param expected: The expected data
        :type expected: dict
        :param actual: The dictionary to check
        :type actual: dict
        :raises: :py:class:`AssertionError`
        """
        self.assertTrue(isinstance(expected, dict))
        self.assertTrue(isinstance(actual, dict))

        for k,v in expected.items():
            self.assertIn(k, actual)

            if isinstance(v, dict):
                self.assertRecursiveDictContains(v, actual[k])
            else:
                self.assertEqual(v, actual[k])

    def test_true_assertRecursiveDictContains(self):
        expected = { 'foo': 'bar',
                     'baz': { 'x': 1,
                              'y': 2}}
        actual = { 'extra': 'data',
                   'foo': 'bar',
                   'baz': { 'x': 1,
                            'y': 2,
                            'more': 'extradata'}}

        self.assertRecursiveDictContains(expected, actual)

    def test_false_assertRecursiveDictContains(self):
        expected = { 'foo': 'bar',
                     'baz': { 'x': 1,
                              'y': 2}}
        actual = { 'extra': 'data',
                   'baz': { 'x': 1,
                            'y': 2,
                            'more': 'extradata'}}

        try:
            self.assertRecursiveDictContains(expected, actual)
        except AssertionError:
            pass

class ContentTests(MirrorsTestCase):
    fixtures = ['content.json']

    def test_get_binary_data(self):
        c = Content.objects.get(slug='test-content-1')
        self.assertEqual(c.binary_data, b'this is the second revision')

    def test_get_binary_data_failure(self):
        c = Content.objects.get(slug='content-with-no-revisions')
        self.assertEqual(c.binary_data, None)


class URLTests(MirrorsTestCase):
    def test_content_urls(self):
        self.assertEqual(reverse('mirrors.views.get_content',
                                 args=('slug',)),
                         '/content/slug')
        self.assertEqual(reverse('mirrors.views.get_content_data',
                                 args=('slug',)),
                         '/content/slug/data')

    def test_content_revision_urls(self):
        self.assertEqual(reverse('mirrors.views.get_content_revision',
                                 args=('slug', 1)),
                         '/content/slug/revision/1')
        self.assertEqual(reverse('mirrors.views.get_content_revision_data',
                                 args=('slug', 1)),
                         '/content/slug/revision/1/data')


class AuthTests(MirrorsTestCase):
    fixtures = ['content.json', 'users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='testuser', password='password')
        self.c_noauth = Client()

    def test_client_authorization(self):
        self.assertTrue(self.c.is_authenticated())
        self.assertFalse(self.c_noauth.is_authenticated())

    def test_get_content_noauth(self):
        r = self.c_noauth.get('/content/test-content-1')
        self.assertEqual(r.status_code, 401)

    def test_get_nonexistent_content_noauth(self):
        r = self.c_noauth.get('/content/no-such-content')
        self.assertEqual(r.status_code, 401)

    def test_get_content_auth(self):
        r = self.c_noauth.get('/content/test-content-1')
        self.assertEqual(r.status_code, 200)

    def test_post_content_auth(self):
        self.fail('Test not yet implemented')

    def test_post_content_noauth(self):
        self.fail('Test not yet implemented')

    def test_patch_content_auth(self):
        self.fail('Test not yet implemented')

    def test_patch_content_noauth(self):
        self.fail('Test not yet implemented')

    def test_delete_content_auth(self):
        self.fail('Test not yet implemented')

    def test_delete_content_noauth(self):
        self.fail('Test not yet implemented')

    def test_put_content_auth(self):
        self.fail('Test not yet implemented')

    def test_put_content_noauth(self):
        self.fail('Test not yet implemented')

