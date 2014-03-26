import json
import hashlib

from django.core.management import call_command
from django.core.urlresolvers import resolve, reverse
from django.db import transaction
from django.test import TestCase, Client

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

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


class ComponentDataTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_get_binary_data(self):
        c = Component.objects.get(slug='test-component-with-multiple-revisions')
        self.assertEqual(c.binary_data, b'this is the second revision')

    def test_get_binary_data_failure(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')
        self.assertEqual(c.binary_data, None)


class ComponentRevisionTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_new_revision_first(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        c.new_revision(data=b'this is a new revision', metadata=json.dumps({
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
        c = Component.objects.get(slug='component-with-binary-data')
        num_orig_components = c.revisions.count()

        cr = c.new_revision(b'this is a new revision', json.dumps({
            'title': 'test component with no revisions'
        }))


        cr = c.revisions.all().order_by('-revision_number').first()
        self.assertEqual(cr.metadata['title'],
                         'test component with no revisions')
        self.assertEqual(cr.revision_number, num_orig_components+1)

    def test_new_revision_no_data(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        with self.assertRaises(ValueError):
            cr = c.new_revision()


class ComponentAttributeTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_get_attribute(self):
        c = Component.objects.get(slug='test-component-with-multiple-levels-sub-1-2')
        c_2 = c.get_attribute('regular_attr')
        self.assertEqual(c_2.slug, 'test-component-with-multiple-levels-sub-1');

    def test_get_attribute_list(self):
        c = Component.objects.get(slug='component-with-list-attribute')
        attr_list = c.get_attribute('my_list_attr')

        self.assertEqual(len(attr_list), 3)
        
    def test_get_attribute_nonexistent(self):
        c = Component.objects.get(slug='test-component-1')
        with self.assertRaises(KeyError):
            c_2 = c.get_attribute('no-such-attribute')

    def test_new_attribute(self):
        c = Component.objects.get(slug='component-with-list-attribute')
        c_2 = Component.objects.get(slug='test-component-1')

        with self.assertRaises(ComponentAttribute.DoesNotExist):
            ComponentAttribute.objects.get(parent=c, child=c_2)

        c.new_attribute('new_attribute_name', c_2)

        ca = c.attributes.get(parent=c, child=c_2)
        self.assertEqual(ca.name, 'new_attribute_name')

    def test_new_attribute_None_child(self):
        c = Component.objects.get(slug='test-component-1')

        with self.assertRaises(ValueError):
            c.new_attribute('subcomponent', None)

    def test_new_attribute_self_child(self):
        c = Component.objects.get(slug='test-component-with-one-attribute')

        with self.assertRaises(ValueError):
            c.new_attribute('selfcomponent', c)

    def test_new_attribute_illegal_name(self):
        c = Component.objects.get(slug='test-component-1')
        c_2 = Component.objects.get(slug='attribute-1')

        with self.assertRaises(KeyError):
            c.new_attribute('s nstubcomponent', c_2)

        with self.assertRaises(KeyError):
            c.new_attribute('-snth', c_2)

        with self.assertRaises(KeyError):
            c.new_attribute('snth$', c_2)

    def test_new_attribute_legal_names(self):
        c = Component.objects.get(slug='test-component-1')
        c_2 = Component.objects.get(slug='attribute-1')

        c.new_attribute('x', c_2)
        c.new_attribute('aoesnuthoaue', c_2)
        c.new_attribute('23eonth8', c_2)
        c.new_attribute('aeoutns-2342e', c_2)

        self.assertEqual(c.attributes.filter(name='x').count(), 1)
        self.assertEqual(c.attributes.filter(name='aoesnuthoaue').count(), 1)
        self.assertEqual(c.attributes.filter(name='23eonth8').count(), 1)
        self.assertEqual(c.attributes.filter(name='aeoutns-2342e').count(), 1)


    def test_new_attribute_creates_list(self):
        c = Component.objects.get(slug='test-component-with-one-attribute')
        c_2 = Component.objects.get(slug='attribute-2')

        c.new_attribute('my_attribute', c_2, 50)

        self.assertEqual(c.attributes.filter(name='my_attribute').count(), 2)


# class URLTests(MirrorsTestCase):
#     def test_component_urls(self):
#         self.assertEqual(reverse('mirrors.views.get_component',
#                                  args=('slug',)),
#                          '/slug')
#         self.assertEqual(reverse('mirrors.views.get_component_data',
#                                  args=('slug',)),
#                          '/slug/data')

#     def test_component_revision_urls(self):
#         self.assertEqual(reverse('mirrors.views.get_component_revision',
#                                  args=('slug', 1)),
#                          '/slug/revision/1')
#         self.assertEqual(reverse('mirrors.views.get_component_revision_data',
#                                  args=('slug', 1)),
#                          '/slug/revision/1/data')


class RESTAPITests(APITestCase):
    fixtures = ['users.json', 'serializer.json']
    def setUp(self):
        self.client = APIClient()

    def test_get_component_resource(self):
        res = self.client.get('/component/test-component-with-no-attributes')
        
        self.assertEqual(res.status_code, 200)

        content = json.loads(res.content)
        self.assertEqual(content['slug'], 'test-component-with-no-attributes')
        self.assertEqual(
            content['uri'],
            '/component/test-component-with-no-attributes/data.md')
        self.assertEqual(content['content_type'], 'application/x-markdown')                                 
        self.assertEqual(content['schema_name'], 'article')
        self.assertEqual(content['metadata'], {
            "title": "test component with no attributes",
            "description": "this is a test article"
        })

    def test_get_component_with_attribute(self):
        res = self.client.get('/component/test-component-with-one-named-attribute')

        self.assertEqual(res.status_code, 200)

        content = json.loads(res.content)
        self.assertEqual(content['slug'], 'test-component-with-one-named-attribute')
        self.assertIn('my_named_attribute', content)
        self.assertTrue(isinstance(content['my_named_attribute'], dict))
        # TODO: test that the attribute is attribute-1

    def test_get_component_with_attribute_list(self):
        res = self.client.get('/component/test-component-with-list-attribute')
        self.assertEqual(res.status_code, 200)

        content = json.loads(res.content)
        self.assertEqual(content['slug'], 'test-component-with-list-attribute')
        self.assertIn('my_list_attribute', content)
        self.assertTrue(isinstance(content['my_list_attribute'], list))
        # TODO: test that the list is in the correct order

#     def test_get_no_auth(self):
#         url = reverse('view-component', kwargs={
#             'component_slug': 'test-component-1'
#         })
#         res = self.client_noauth.get(url)
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     ### tests against /component
#     def test_get_component_list(self):
#         url = reverse('view-component')
#         res = self.client.get(url)
#         self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

#     ### tests against /component/<slug-id>
#     def test_get_component(self):
#         url = reverse('view-component', kwargs={
#             'component_slug': 'test-component-1'
#         })
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, {
#             'schema_name': 'test-schema',
#             'publish_date': '2014-01-30T19:32:34.555Z',
#             'slug': 'test-component-1',
#             'content_type': 'none',
#             'metadata': {
#                 'author': 'author one',
#                 'title': 'test component 1'
#             },
#             'attributes': {},
#             'members': []
#         })

#     def test_get_nonexistent_component(self):
#         url = reverse('view-component', kwargs={
#             'component_slug': 'no-such-component'
#         })
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

#     def test_put_component(self):
#         put_data = {
#             'schema_name': 'test-schema',
#             'publish_date': '2014-01-30T19:32:34.555Z',
#             'content_type': 'none',
#             'metadata': {
#                 'author': 'author one',
#                 'title': 'test component 1'
#             }
#         }
#         expected_resp_data = {
#             'slug': 'new-component',
#             'schema_name': 'test-schema',
#             'publish_date': '2014-01-30T19:32:34.555Z',
#             'content_type': 'none',
#             'metadata': {
#                 'author': 'author one',
#                 'title': 'test component 1'
#             },
#             'attributes': {},
#             'members': []
#         }

#         url = reverse('view-component',
#                       kwargs={'component_slug': 'new-component'})
#         res = self.client.put(url, put_data, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(res.data, expected_resp_data)

#     def test_put_conflicting_name_component(self):
#         put_data = {
#             'schema_name': 'test-schema',
#             'publish_date': '2014-01-30T19:32:34.555Z',
#             'content_type': 'none',
#             'metadata': {
#                 'author': 'author one',
#                 'title': 'test component 1'
#             }
#         }

#         url = reverse('view-component',
#                       kwargs={'component_slug': 'test-component-1'})
#         res = self.client.put(url, put_data, format='json')

#         self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

#     def test_patch_component(self):
#         patch_data = {
#             'content_type': 'article'
#         }
#         expected_resp_data = {
#             'schema_name': 'test-schema',
#             'publish_date': '2014-01-30T19:32:34.555Z',
#             'slug': 'test-component-1',
#             'content_type': 'article',
#             'metadata': {
#                 'author': 'author one',
#                 'title': 'test component 1'
#             }
#         }

#         url = reverse('view-component',
#                       kwargs={'component_slug': 'test-component-1'})
#         res = self.client.patch(url, patch_data, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, expected_resp_data)

#     def test_patch_404_component(self):
#         patch_data = {
#             'content_type': 'article'
#         }
#         url = reverse('view-component',
#                       kwargs={'component_slug': 'no-such-component'})
#         res = self.client.patch(url, patch_data, format='json')

#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

#     def test_patch_component_no_changes(self):
#         patch_data = {
#             'content_type': 'none'
#         }
#         expected_resp_data = {
#             'schema_name': 'test-schema',
#             'publish_date': '2014-01-30T19:32:34.555Z',
#             'slug': 'test-component-1',
#             'content_type': 'none',
#             'metadata': {
#                 'author': 'author one',
#                 'title': 'test component 1'
#             }
#         }

#         url = reverse('view-component',
#                       kwargs={'component_slug': 'test-component-1'})
#         res = self.client.patch(url, patch_data, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, expected_resp_data)

#     def test_delete_component(self):
#         url = reverse('view-component',
#                       kwargs={'component_slug': 'test-component-1'})
#         res = self.client.patch(url, format='json')

#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

#     def test_delete_404_component(self):
#         url = reverse('view-component',
#                       kwargs={'component_slug': 'no-such-component'})
#         res = self.client.delete(url, format='json')

#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

#     ### tests against /component/<slug-id>/data
#     def test_get_component_data(self):
#         self.fail('not implemented yet')

#     def test_get_component_without_data(self):
#         self.fail('not implemented yet')

#     def test_put_component_data(self):
#         self.fail('not implemented yet')

#     def test_post_component_data(self):
#         self.fail('not implemented yet')

#     ### tests against /component/<slug-id>/rev
#     def test_get_revision_list(self):
#         self.fail('not implemented yet')

#     def test_post_revision_list(self):
#         self.fail('not implemented yet')

#     ### tests against /component/<slug-id>/rev/<rev-num>
#     def test_get_revision(self):
#         self.fail('not implemented yet')

#     def test_get_404_revision(self):
#         self.fail('not implemented yet')

#     def test_delete_revision(self):
#         self.fail('not implemented yet')

#     ### tests against /component/<slug-id>/attribute
#     def test_get_attribute_list(self):
#         self.fail('not implementeyet')

#     def test_get_empty_attribute_list(self):
#         self.fail('not implemented yet')

#     ### tests against /component/<slug-id>/attribute/<attr-name>
#     def test_put_new_attribute(self):
#         self.fail('not implemented yet')

#     def test_get_attribute(self):
#         self.fail('not implemented yet')

#     def test_put_conflicting_attribute(self):
#         self.fail('not implemented yet')

#     def test_get_404_attribute(self):
#         self.fail('not implemented yet')

#     def test_delete_attribute(self):
#         self.fail('not implemented yet')

#     def test_patch_attribute(self):
#         self.fail('not implemented yet')

#     ### tests against /component/<slug-id>/member
#     def test_get_member_list(self):
#         self.fail('not implemented yet')

#     def test_post_member(self):
#         self.fail('not implemented yet')

#     ### tests against /component/<slug-id>/member/<member-index>
#     def test_get_member(self):
#         self.fail('not implemented yet')

#     def test_get_404_member(self):
#         self.fail('not implemented yet')

#     def test_put_new_member(self):
#         self.fail('not implemented yet')

#     def test_put_overwrite_member(self):
#         self.fail('not implemented yet')

#     def test_patch_member(self):
#         self.fail('not implemented yet')

#     def test_delete_member(self):
#         self.fail('not implemented yet')
