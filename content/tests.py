import json
import hashlib

from django.test import TestCase
from django.core.urlresolvers import resolve, reverse
from django.test import Client

from content import urls as content_url
from content.models import Content, ContentRevision

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
        self.assertEqual(reverse('content.views.get_content',
                                 args=('slug',)),
                         '/content/slug')
        self.assertEqual(reverse('content.views.get_content_data',
                                 args=('slug',)),
                         '/content/slug/data')

    def test_content_revision_urls(self):
        self.assertEqual(reverse('content.views.get_content_revision',
                                 args=('slug', 1)),
                         '/content/slug/revision/1')
        self.assertEqual(reverse('content.views.get_content_revision_data',
                                 args=('slug', 1)),
                         '/content/slug/revision/1/data')


class APITests(MirrorsTestCase):
    fixtures = ['content.json', 'users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='testuser', password='password')
        self.c_noauth = Client()

    def test_get_content_noauth(self):
        r = self.c_noauth.get('/content/test-content-1')
        self.assertEqual(r.status_code, 401)

        r_data = json.loads(r.content)
        self.assertDictEqual(r_data, {'error': True,
                                      'message': 'Not authorized'})

    def test_get_content_no_members(self):
        r = self.c.get('/content/test-content-1')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content Type'], 'application/json')

        r_data = json.loads(r.content)
        self.assertDictContainsSubset(
            {'slug': 'test-content-1',
             'members': []},
            r_data)
        self.assertDictContainsSubset(
            {'title': 'test content 1',
             'author': 'bobby tables'},
            r_data['metadata'])

    def test_get_content_with_members(self):
        r = self.c.get('/content/content-with-members')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content Type'], 'application/json')

        r_data = json.loads(r.content)
        self.assertDictContainsSubset(
            {'slug': 'content-with-members',
             'members': ['content-with-members-member']},
            r_data)
        self.assertDictContainsSubset(
            {'title': 'this content has members',
             'author': 'bobby tables'},
            r_data['metadata'])

    def test_get_no_such_content(self):
        r = self.c.get('/content/no-such-content')
        self.assertEqual(r.status_code, 404)

    def test_get_content_plaintext_binary_data(self):
        r = self.c.get('/content/test-plain-text-content/data')

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content Type'], 'text/plain')
        self.assertEqual(r.content, 'this is plaintext data')

    def test_get_content_image_binary_data(self):
        # this image was made by checkyourhead90 and shared under the
        # creative commons attribution/no derivitives license
        # link:
        # http://farm4.staticflickr.com/3783/12177244376_15840a9a58_z_d.jpg
        # the image is in the fixtures directory
        r = self.c.get('/content/test-jpeg-content/data')
        expected_hash = '9aad57a37d4358e8cbcd13ee594099e8'

        self.assertEqual(r.status_code, 200)
        self.assertEqual(hashlib.md5(r.content).hexdigest(),
                         expected_hash)

    def test_get_content_revision(self):
        r = self.c_noauth.get('/content/test-content-1/revision/1')
        self.assertEqual(r['Content Type'], 'text/plain')
        self.assertEqual(r.content, 'this is the first revision')

    def test_get_content_no_such_revision(self):
        r = self.c.get('/content/content-with-no-revisions')
        self.assertEqual(r.status_code, 404)

    def test_put_content(self):
        put_data = {'slug': 'test-put-content',
                    'metadata': {'title': 'test put content',
                                 'author': 'test put content author'},
                    'schema': {'schemaname': 'fake'}}
        r = self.c.put('/content/test-put-content', put_data)
        self.assertEqual(r.status_code, 201)

        r_data = json.loads(r.content)
        self.assertIn('success', r_data)
        self.assertIn('new_object', r_data)

        self.assertTrue(r_data['success'])

        obj_data = r_data['new_object']
        self.assertDictContainsSubset({'slug': 'test-put-content'}, obj_data)
        self.assertDictContainsSubset(
            {'title': 'test put content',
             'author': 'test put content author'},
            obj_data['metadata'])
        self.assertDictContainsSubset({'schemaname': 'fake'},
                                      obj_data['schema'])

    def test_put_incomplete_content(self):
        put_data = {'slug': 'test-incomplete-put-content'}
        r = self.c.put('/content/test-incomplete-put-content', put_data)
        self.assertEqual(r.status_code, 500)

        r_data = json.loads(r.content)
        self.assertDictEqual(r_data, {'error': True,
                                      'message': 'Incomplete data'})

    def test_patch_content(self):
        patch_data = {'metadata': {'author': 'patched author'}}
        r = self.c.patch('/content/test-content-1', patch_data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content Type'], 'application/json')

        r_data = json.loads(r.content)['object']
        self.assertDictContainsSubset(
            {'slug': 'test-content-1',
             'members': []},
            r_data)

        self.assertDictContainsSubset(
            {'title': 'test content 1',
             'author': 'patched author'},
            r_data['metadata'])

    def test_patch_missing_content(self):
        patch_data = {'metadata': {'author': 'patched author'}}
        r = self.c.patch('/content/test-patch-missing-content', patch_data)
        self.assertEqual(r.status_code, 404)

    def test_delete_content(self):
        r = self.c.delete('/content/test-delete-content')
        self.assertEqual(r.status_code, 204)

        r = self.c.get('/content/test-delete-content')
        self.assertEqual(r.status_code, 404)

    def test_delete_missing_content(self):
        r = self.c.delete('/content/test-delete-missing-content')
        self.assertEqual(r.status_code, 404)
