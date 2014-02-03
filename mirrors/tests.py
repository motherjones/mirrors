import json
import hashlib

from django.core.urlresolvers import resolve, reverse
from django.db import transaction
from django.test import TestCase, Client

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

        for k, v in expected.items():
            self.assertIn(k, actual)

            if isinstance(v, dict):
                self.assertRecursiveDictContains(v, actual[k])
            else:
                self.assertEqual(v, actual[k])

    def test_true_assertRecursiveDictContains(self):
        expected = {'foo': 'bar',
                    'baz': {'x': 1,
                            'y': 2}}
        actual = {'extra': 'data',
                  'foo': 'bar',
                  'baz': {'x': 1,
                          'y': 2,
                          'more': 'extradata'}}

        self.assertRecursiveDictContains(expected, actual)

    def test_false_assertRecursiveDictContains(self):
        expected = {'foo': 'bar',
                    'baz': {'x': 1,
                            'y': 2}}
        actual = {'extra': 'data',
                  'baz': {'x': 1,
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
        c = Content.objects.get(slug='test-content-with-no-revisions')
        self.assertEqual(c.binary_data, None)


class ContentRevisionTests(MirrorsTestCase):
    fixtures = ['content.json']

    def test_new_revision_first(self):
        c = Content.objects.get(slug='test-content-with-no-revisions')
        c.new_revision(b'this is a new revision', json.dumps({
            'title': 'test content with no revisions'
        }))

        cr = c.revisions.get(revision_number=1)

        self.assertEqual(c.revisions.count(), 1)
        self.assertEqual(cr.content, c)
        self.assertEqual(cr.data, b'this is a new revision')

    def test_new_revision_not_first(self):
        c = Content.objects.get(slug='test-content-1')
        cr = c.new_revision(b'this is a new revision', json.dumps({
            'title': 'test content with no revisions'
        }))

        self.assertEqual(cr.content, c)
        self.assertEqual(cr.metadata['title'],
                         'test content with no revisions')

    def test_new_revision_no_data(self):
        c = Content.objects.get(slug='test-content-with-no-revisions')

        with self.assertRaises(ValueError):
            cr = c.new_revision()


class ContentAttributeTests(MirrorsTestCase):
    fixtures = ['content.json']

    def test_get_attribute(self):
        self.fail('Not yet implemented')

    def test_get_attribute_nonexistent(self):
        self.fail('Not yet implemented')

    def test_new_attribute_nonexistent(self):
        self.fail('Not yet implemented')

    def test_new_attribute_overwrite(self):
        self.fail('Not yet implemented')


class ContentMemberTests(MirrorsTestCase):
    fixtures = ['content.json']

    def test_new_member_append_empty_list(self):
        c = Content.objects.get(slug='test-content-with-no-members')
        c_2 = Content.objects.get(slug='test-content-with-members')

        cm = c.new_member(c_2)

        self.assertEqual(c.members.count(), 1)
        self.assertEqual(c.members.all()[0].slug, 'test-content-with-members')
        self.assertEqual(cm.order, ContentMembers.max_index/2)

    def test_new_member_append_nonempty_list(self):
        self.fail('Not yet implemented')

    def test_new_member_preprend(self):
        self.fail('Not yet implemented')

    def test_new_member_bisect_nonempty_list(self):
        self.fail('Not yet implemented')

    def test_new_member_bisect_empty_list(self):
        self.fail('Not yet implemented')


class URLTests(MirrorsTestCase):
    def test_content_urls(self):
        self.assertEqual(reverse('mirrors.views.get_content',
                                 args=('slug',)),
                         '/slug')
        self.assertEqual(reverse('mirrors.views.get_content_data',
                                 args=('slug',)),
                         '/slug/data')

    def test_content_revision_urls(self):
        self.assertEqual(reverse('mirrors.views.get_content_revision',
                                 args=('slug', 1)),
                         '/slug/revision/1')
        self.assertEqual(reverse('mirrors.views.get_content_revision_data',
                                 args=('slug', 1)),
                         '/slug/revision/1/data')
