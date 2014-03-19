import json
import hashlib

from django.core.management import call_command
from django.core.urlresolvers import resolve, reverse
from django.db import transaction
from django.test import TestCase, Client

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from mirrors import urls as content_url
from mirrors.models import *


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


class ComponentTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_get_binary_data(self):
        c = Component.objects.get(slug='test-component-1')
        self.assertEqual(c.binary_data, b'this is the second revision')

    def test_get_binary_data_failure(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')
        self.assertEqual(c.binary_data, None)


class ComponentRevisionTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_new_revision_first(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')
        c.new_revision(b'this is a new revision', json.dumps({
            'title': 'test component with no revisions'
        }))

        cr = c.revisions.get(revision_number=1)

        self.assertEqual(c.revisions.count(), 1)
        self.assertEqual(cr.component, c)
        self.assertEqual(cr.data, b'this is a new revision')

    def test_new_revision_first_only_metadata(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        with self.assertRaises(ValueError):
            c.new_revision(metadata=json.dumps({
                'title': 'this thing should fail!'
            }))

    def test_new_revision_not_first(self):
        c = Component.objects.get(slug='test-component-1')
        cr = c.new_revision(b'this is a new revision', json.dumps({
            'title': 'test component with no revisions'
        }))

        self.assertEqual(cr.component, c)
        self.assertEqual(cr.metadata['title'],
                         'test component with no revisions')

    def test_new_revision_no_data(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        with self.assertRaises(ValueError):
            cr = c.new_revision()


class ComponentAttributeTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_get_attribute(self):
        c = Component.objects.get(slug='test-component-with-attributes')
        c_2 = c.get_attribute('subcomponent')
        self.assertEqual(c_2.slug, 'test-component-with-attributes-sub-1')

    def test_get_attribute_nonexistent(self):
        c = Component.objects.get(slug='test-component-with-attributes')
        with self.assertRaises(KeyError):
            c_2 = c.get_attribute('no-such-attribute')

    def test_new_attribute(self):
        c = Component.objects.get(slug='test-component-with-attributes')
        c_2 = Component.objects.get(slug='test-component-1')

        with self.assertRaises(ComponentAttribute.DoesNotExist):
            ComponentAttribute.objects.get(parent=c, child=c_2)

        c.new_attribute('new_attribute_name', c_2)

        ca = ComponentAttribute.objects.get(parent=c, child=c_2)
        self.assertEqual(ca.name, 'new_attribute_name')

    def test_new_attribute_overwrite(self):
        c = Component.objects.get(slug='test-component-with-attributes')
        c_2 = Component.objects.get(slug='test-component-1')
        c.new_attribute('subcomponent', c_2)

        ca = ComponentAttribute.objects.get(parent=c, child=c_2)
        self.assertEqual(ca.name, 'subcomponent')

    def test_new_attribute_None_child(self):
        c = Component.objects.get(slug='test-component-with-attributes')

        with self.assertRaises(ValueError):
            c.new_attribute('subcomponent', None)

    def test_new_attribute_self_child(self):
        c = Component.objects.get(slug='test-component-with-attributes')

        with self.assertRaises(ValueError):
            c.new_attribute('subcomponent', c)

    def test_new_attribute_illegal_name(self):
        c = Component.objects.get(slug='test-component-with-attributes')
        c_2 = Component.objects.get(slug='test-component-1')

        with self.assertRaises(KeyError):
            c.new_attribute('s nstubcomponent', c_2)

        with self.assertRaises(KeyError):
            c.new_attribute('snth$', c_2)


class URLTests(MirrorsTestCase):
    def test_component_urls(self):
        self.assertEqual(reverse('mirrors.views.get_component',
                                 args=('slug',)),
                         '/slug')
        self.assertEqual(reverse('mirrors.views.get_component_data',
                                 args=('slug',)),
                         '/slug/data')

    def test_component_revision_urls(self):
        self.assertEqual(reverse('mirrors.views.get_component_revision',
                                 args=('slug', 1)),
                         '/slug/revision/1')
        self.assertEqual(reverse('mirrors.views.get_component_revision_data',
                                 args=('slug', 1)),
                         '/slug/revision/1/data')


class RESTAPITests(APITestCase):
    fixtures = ['api.json', 'users.json']

    def setUp(self):
        self.token = Token.objects.get(user__username='test_admin')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client_noauth = APIClient()

    def test_get_no_auth(self):
        url = reverse('view-component', kwargs={
            'component_slug': 'test-component-1'
        })
        res = self.client_noauth.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    ### tests against /component
    def test_get_component_list(self):
        url = reverse('view-component')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ### tests against /component/<slug-id>
    def test_get_component(self):
        url = reverse('view-component', kwargs={
            'component_slug': 'test-component-1'
        })
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'schema_name': 'test-schema',
            'publish_date': '2014-01-30T19:32:34.555Z',
            'slug': 'test-component-1',
            'content_type': 'none',
            'metadata': {
                'author': 'author one',
                'title': 'test component 1'
            },
            'attributes': {},
            'members': []
        })

    def test_get_nonexistent_component(self):
        url = reverse('view-component', kwargs={
            'component_slug': 'no-such-component'
        })
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_component(self):
        put_data = {
            'schema_name': 'test-schema',
            'publish_date': '2014-01-30T19:32:34.555Z',
            'content_type': 'none',
            'metadata': {
                'author': 'author one',
                'title': 'test component 1'
            }
        }
        expected_resp_data = {
            'slug': 'new-component',
            'schema_name': 'test-schema',
            'publish_date': '2014-01-30T19:32:34.555Z',
            'content_type': 'none',
            'metadata': {
                'author': 'author one',
                'title': 'test component 1'
            },
            'attributes': {},
            'members': []
        }

        url = reverse('view-component',
                      kwargs={'component_slug': 'new-component'})
        res = self.client.put(url, put_data, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, expected_resp_data)

    def test_put_conflicting_name_component(self):
        self.fail('not implemented yet')

    def test_post_to_component(self):
        self.fail('not implemented yet')

    def test_patch_component(self):
        self.fail('not implemented yet')

    def test_patch_component_no_changes(self):
        self.fail('not implemented yet')

    def test_delete_component(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/data
    def test_get_component_data(self):
        self.fail('not implemented yet')

    def test_get_component_without_data(self):
        self.fail('not implemented yet')

    def test_put_component_data(self):
        self.fail('not implemented yet')

    def test_post_component_data(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/rev
    def test_get_revision_list(self):
        self.fail('not implemented yet')

    def test_post_revision_list(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/rev/<rev-num>
    def test_get_revision(self):
        self.fail('not implemented yet')

    def test_get_404_revision(self):
        self.fail('not implemented yet')

    def test_delete_revision(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/attribute
    def test_get_attribute_list(self):
        self.fail('not implementeyet')

    def test_get_empty_attribute_list(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/attribute/<attr-name>
    def test_put_new_attribute(self):
        self.fail('not implemented yet')

    def test_get_attribute(self):
        self.fail('not implemented yet')

    def test_put_conflicting_attribute(self):
        self.fail('not implemented yet')

    def test_get_404_attribute(self):
        self.fail('not implemented yet')

    def test_delete_attribute(self):
        self.fail('not implemented yet')

    def test_patch_attribute(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/member
    def test_get_member_list(self):
        self.fail('not implemented yet')

    def test_post_member(self):
        self.fail('not implemented yet')

    ### tests against /component/<slug-id>/member/<member-index>
    def test_get_member(self):
        self.fail('not implemented yet')

    def test_get_404_member(self):
        self.fail('not implemented yet')

    def test_put_new_member(self):
        self.fail('not implemented yet')

    def test_put_overwrite_member(self):
        self.fail('not implemented yet')

    def test_patch_member(self):
        self.fail('not implemented yet')

    def test_delete_member(self):
        self.fail('not implemented yet')
