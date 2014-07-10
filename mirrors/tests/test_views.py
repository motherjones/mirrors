import hashlib
import json
import os

import jsonschema

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from rest_framework import status
from rest_framework.test import APITestCase

from mirrors import components
from mirrors.models import Component


class ComponentViewTest(APITestCase):
    fixtures = ['users.json', 'serializer.json']

    def setUp(self):
        self.valid_component = {
            'content_type': 'application/x-markdown',
            'schema_name': 'article',
            'metadata': json.dumps({
                'title': 'Valid component'
            })
        }

    def test_get_component(self):
        url = reverse('component-detail', kwargs={
            'slug': 'test-component-with-one-named-attribute'
        })

        res = self.client.get(url)
        self.assertTrue(status.is_success(res.status_code))

        data = json.loads(res.content.decode('UTF-8'))
        self.assertEqual(data['schema_name'], 'schema name')
        self.assertEqual(data['created_at'], '2014-02-06T00:03:40.660Z')
        self.assertEqual(data['updated_at'], '2014-02-06T00:03:40.660Z')
        self.assertEqual(data['slug'],
                         'test-component-with-one-named-attribute')
        self.assertEqual(data['content_type'], 'none')
        self.assertEqual(data['metadata']['title'],
                         'test component with a single named attribute')
        self.assertEqual(data['metadata']['author'], 'author one')
        self.assertEqual(len(data['attributes']), 1)
        self.assertIn('my_named_attribute', data['attributes'])

        attribute = data['attributes']['my_named_attribute']
        self.assertEqual(attribute['schema_name'], 'schema name')
        self.assertEqual(attribute['created_at'], '2014-02-06T00:03:40.660Z')
        self.assertEqual(attribute['updated_at'], '2014-02-06T00:03:40.660Z')
        self.assertEqual(attribute['slug'], 'attribute-1')
        self.assertEqual(attribute['content_type'], 'none')
        self.assertEqual(attribute['metadata']['author'], 'attribute author')
        self.assertEqual(attribute['metadata']['title'], 'attribute 1')
        self.assertEqual(len(attribute['attributes']), 0)

    def test_get_404_component(self):
        url = reverse('component-detail', kwargs={
            'slug': 'no-such-component-here'
        })

        res = self.client.get(url)
        self.assertTrue(res.status_code, 404)

    def test_post_new_component(self):
        url = reverse('component-list')
        self.valid_component['slug'] = 'my-new-slug'

        res = self.client.post(url, self.valid_component)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertEqual(data['schema_name'], 'article')
        self.assertEqual(data['content_type'], 'application/x-markdown')
        self.assertEqual(data['slug'], 'my-new-slug')

        self.assertIn('metadata', data)
        self.assertEqual(data['metadata']['title'], 'Valid component')

    def test_post_new_component_used_name(self):
        url = reverse('component-list')
        self.valid_component['slug'] = 'this-is-for-testing-on'

        res = self.client.post(url, self.valid_component)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('slug', data)
        self.assertEqual(data['slug'],
                         ['Component with this Slug already exists.'])

    def test_post_new_component_missing_data(self):
        url = reverse('component-list')

        res = self.client.post(url, self.valid_component)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(res.content.decode('UTF-8'))

        self.assertEqual(len(data.keys()), 1)
        self.assertIn('slug', data)
        self.assertEqual(data['slug'], ['This field is required.'])

    def test_post_new_component_invalid_name(self):
        url = reverse('component-list')
        self.valid_component['slug'] = 'not a valid slug'
        res = self.client.post(url, self.valid_component)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('slug', data)
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data['slug'],
                         ["Enter a valid 'slug' consisting of letters, "
                          "numbers, underscores or hyphens."])

    def test_patch_404_component(self):
        url = reverse('component-detail', kwargs={
            'slug': 'doesnt-exist'
        })

        res = self.client.patch(url, {'content_type': 'text/plain'})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_component_one_change(self):
        url = reverse('component-detail', kwargs={
            'slug': 'this-is-for-testing-on'
        })

        res = self.client.patch(url, {'content_type': 'text/plain'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = json.loads(res.content.decode('UTF-8'))

        self.assertEqual(data['schema_name'], 'article')
        self.assertEqual(data['content_type'], 'text/plain')
        self.assertEqual(data['slug'], 'this-is-for-testing-on')
        self.assertEqual(data['metadata']['title'], 'thing thing thing')

    def test_patch_component_multiple_changes(self):
        url = reverse('component-detail', kwargs={
            'slug': 'this-is-for-testing-on'
        })

        res = self.client.patch(url, {
            'content_type': 'text/plain',
            'schema_name': 'patched'
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = json.loads(res.content.decode('UTF-8'))

        self.assertEqual(data['schema_name'], 'patched')
        self.assertEqual(data['content_type'], 'text/plain')
        self.assertEqual(data['slug'], 'this-is-for-testing-on')
        self.assertEqual(data['metadata']['title'], 'thing thing thing')

    def test_patch_component_not_a_dict(self):
        url = reverse('component-detail', kwargs={
            'slug': 'this-is-for-testing-on'
        })

        res = self.client.patch(url, "invalid data")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_component_invalid_data(self):
        url = reverse('component-detail', kwargs={
            'slug': 'this-is-for-testing-on'
        })

        res = self.client.patch(url, {
            'metadata': 3
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertEqual(data, {
            'metadata': ['This field must be a JSON object']
        })

    def test_patch_component_metadata(self):
        url = reverse('component-detail', kwargs={
            'slug': 'this-is-for-testing-on'
        })

        res = self.client.patch(url, {
            'metadata': {'title': 'updated thing'}
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = json.loads(res.content.decode('UTF-8'))

        self.assertEqual(data['metadata']['title'], 'updated thing')

    def test_delete_component(self):
        url = reverse('component-detail', kwargs={
            'slug': 'this-is-for-testing-on'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_404_component(self):
        url = reverse('component-detail', kwargs={
            'slug': 'doesnt-exist'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ComponentAttributeViewTests(APITestCase):
    fixtures = ['users.json', 'componentattributes.json']

    def test_get_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'my_attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('child', data)
        self.assertEqual(data['child'], 'attribute-1')

    def test_get_404_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'no_such_attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_new_attribute(self):
        url = reverse('component-attribute-list', kwargs={
            'slug': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': 'new_attribute',
                                     'child': 'attribute-4'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('child', data)
        self.assertNotIn('weight', data['child'])
        self.assertEqual(data['child'], 'attribute-4')

    def test_put_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'my_attribute'
        })

        res = self.client.put(url, {'name': 'my_attribute',
                                    'child': 'attribute-2'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('child', data)
        self.assertIn('name', data)
        self.assertEqual(data['name'], 'my_attribute')
        self.assertEqual(data['child'], 'attribute-2')

    def test_put_attribute_invalid_type(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'my_attribute'
        })

        res = self.client.put(url, 'blah')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('error', data)
        self.assertEqual(data['error'],
                         'ComponentAttribute data must be a list or a dict')

    def test_put_attribute_invalid_data(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'my_attribute'
        })

        res = self.client.put(url, {'name': 'my_attribute'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('child', data)
        self.assertEqual(len(data['child']), 1)
        self.assertEqual(data['child'][0], 'This field is required.')

    def test_post_new_attribute_strip_slug(self):
        url = reverse('component-attribute-list', kwargs={
            'slug': 'component-with-regular-attribute'
        })
        res = self.client.post(url, {'name': 'new_attribute',
                                     'child': 'attribute-4',
                                     'slug': 'attribute-4'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_post_new_attribute_invalid_name(self):
        url = reverse('component-attribute-list', kwargs={
            'slug': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': '$not a valid name(',
                                     'child': 'attribute-4'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = json.loads(res.content.decode('UTF-8'))

        self.assertIn('name', data)
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data['name'],
                         ["Enter a valid 'slug' consisting of letters, "
                          "numbers, underscores or hyphens."])

    def test_post_new_attribute_used_name(self):
        url = reverse('component-attribute-list', kwargs={
            'slug': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': 'my_attribute',
                                     'child': 'attribute-4'})

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_post_new_attribute_invalid_component_name(self):
        url = reverse('component-attribute-list', kwargs={
            'slug': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': 'new_attribute',
                                     'child': '#not a valid component name'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(res.content.decode('UTF-8'))

        self.assertIn('child', data)
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data['child'],
                         ["Object with slug=#not a valid component name does "
                          "not exist."])

    def test_post_new_attribute_404_component(self):
        url = reverse('component-attribute-list', kwargs={
            'slug': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': 'new_attribute',
                                     'child': 'no-such-component-name'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(res.content.decode('UTF-8'))

        self.assertIn('child', data)
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data['child'],
                         ['Object with slug=no-such-component-name does not '
                          'exist.'])

    def test_get_attribute_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-list-attribute',
            'name': 'list_attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['child'], 'attribute-3')
        self.assertEqual(data[1]['child'], 'attribute-4')

        self.assertEqual(data[0]['weight'], 100)
        self.assertEqual(data[1]['weight'], 200)

    def test_get_404_attribute_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-list-attribute',
            'name': 'no-such-attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_attribute_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-list-attribute',
            'name': 'list_attribute'
        })

        attribute_list = [{'child': 'attribute-4', 'weight': 200},
                          {'child': 'attribute-3', 'weight': 100},
                          {'child': 'attribute-1', 'weight': 9999}]

        res = self.client.put(url, data=attribute_list)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0]['child'], 'attribute-3')
        self.assertEqual(data[1]['child'], 'attribute-4')
        self.assertEqual(data[2]['child'], 'attribute-1')

        self.assertEqual(data[0]['weight'], 100)
        self.assertEqual(data[1]['weight'], 200)
        self.assertEqual(data[2]['weight'], 9999)

    def test_delete_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'my_attribute'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_404_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-regular-attribute',
            'name': 'no-such-slug'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_attribute_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'slug': 'component-with-list-attribute',
            'name': 'list_attribute'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class ComponentDataViewTest(TestCase):
    fixtures = ['component_data.json']

    def setUp(self):
        self.client = Client()

        self.svg_hash = '01d5a1a9d1452f1b013bfc74da44d52e'
        self.jpeg_hash = '6367446e537b50e363f26e385f47e99d'
        self.md_hash = 'eb867962bfff036e98b5e59dc6153caf'

    def test_get_data(self):
        url = reverse('component-data', kwargs={
            'slug': 'component-with-svg-data'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.get('Content-Type'), 'image/svg+xml')

        md5_hash = hashlib.md5()
        md5_hash.update(res.content)
        self.assertEqual(md5_hash.hexdigest(), self.svg_hash)

    def test_get_data_component_without_data(self):
        url = reverse('component-data', kwargs={
            'slug': 'component-with-no-data'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_data_with_filename(self):
        url = reverse('component-data', kwargs={
            'slug': 'component-with-svg-data-and-metadata-filename'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.get('Content-Disposition'),
                         'inline; filename=einfache_zeitung.svg')

    def test_get_data_without_filename(self):
        url = reverse('component-data', kwargs={
            'slug': 'component-with-svg-data'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.get('Content-Disposition'),
                         'inline; filename=component-with-svg-data')

    def test_post_data(self):
        c = Client()

        url = reverse('component-data', kwargs={
            'slug': 'component-with-no-data'
        })
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '..',
                                                 'fixtures',
                                                 'binary-data',
                                                 'fake_article.md'))

        component = Component.objects.get(slug='component-with-no-data')

        with open(file_path, 'rb') as upload_file:
            # req = rf.post(url, data={'file': upload_file})
            # res = ComponentDataView.post(req)
            res = c.post(url,
                         data={'file': upload_file})

            self.assertTrue(res.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(component.revisions.count(), 1)

            rev = component.revisions.first()
            md5_hash = hashlib.md5()
            md5_hash.update(rev.data)
            self.assertEqual(md5_hash.hexdigest(), self.md_hash)


class ComponentRevisionViewTest(APITestCase):
    fixtures = ['users.json', 'componentrevisions.json']

    def setUp(self):
        self.valid_component = {
            'content_type': 'application/x-markdown',
            'schema_name': 'article',
            'metadata': json.dumps({
                'title': 'Valid component'
            })
        }

    def test_get_component_at_version(self):
        url = reverse('component-revision-detail', kwargs={
            'slug': 'component-with-many-revisions',
            'version': 3
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertEqual(data['schema_name'], 'none')
        self.assertEqual(data['created_at'], '2014-06-09T20:07:40.386Z')
        self.assertEqual(data['updated_at'], '2014-06-09T20:10:20.320Z')
        self.assertEqual(data['slug'], 'component-with-many-revisions')
        self.assertEqual(data['content_type'], 'text/plain')
        self.assertEqual(data['metadata'], {"test": "first metadata"})
        self.assertEqual(len(data['attributes']), 0)

    def test_get_component_data_at_version(self):
        url = reverse('component-revision-data', kwargs={
            'slug': 'component-with-many-revisions',
            'version': 3
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/plain')

        data = res.content.decode('UTF-8')
        self.assertEqual(data, 'second data')

    def test_get_component_data_at_version_with_filename(self):
        url = reverse('component-revision-data', kwargs={
            'slug': 'component-with-data-and-filename',
            'version': 1
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/plain')

        data = res.content.decode('UTF-8')
        self.assertEqual(data, 'this is some data')
        self.assertEqual(res.get('Content-Disposition'),
                         'inline; filename=file.txt')

    def test_get_component_data_at_version_no_data(self):
        url = reverse('component-revision-data', kwargs={
            'slug': 'component-with-no-data',
            'version': 2
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_component_at_404_version(self):
        url = reverse('component-revision-detail', kwargs={
            'slug': 'component-with-many-revisions',
            'version': 999
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ComponentRevisionSummaryViewTests(APITestCase):
    fixtures = ['users.json', 'componentrevisions.json']

    def test_serialize_revision_summary_with_multiple_type_changes(self):
        url = reverse('component-revision-list', kwargs={
            'slug': 'component-with-revision-with-data-and-metadata'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        rev = data[0]
        self.assertTrue(isinstance(rev, dict))
        self.assertEqual(rev['version'], 1)
        self.assertEqual(rev['change_date'], '2014-06-09T19:50:40.797Z')

        self.assertTrue(isinstance(rev['change_types'], list))
        self.assertEqual(len(rev['change_types']), 2)
        self.assertIn('data', rev['change_types'])
        self.assertIn('metadata', rev['change_types'])

    def test_serialize_revision_summary(self):
        url = reverse('component-revision-list', kwargs={
            'slug': 'component-with-two-revisions'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))

        self.assertTrue(isinstance(data, list))
        rev_1 = data[0]
        rev_2 = data[1]

        self.assertTrue(isinstance(rev_1, dict))
        self.assertEqual(rev_1['version'], 1)
        self.assertEqual(rev_1['change_date'], '2014-06-09T19:44:12.459Z')
        self.assertEqual(rev_1['change_types'], ['metadata'])

        self.assertEqual(rev_2['version'], 2)
        self.assertEqual(rev_2['change_date'], '2014-06-09T19:56:42.455Z')
        self.assertEqual(rev_2['change_types'], ['data'])

    def test_serialize_revision_summary_no_revisions(self):
        url = reverse('component-revision-list', kwargs={
            'slug': 'component-with-no-revisions'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ComponentValidityTest(APITestCase):
    fixtures = ['users.json', 'component_validity.json']

    class TestAttributeSchema(components.Component):
        id = 'testattribute'
        schema_title = 'test attribute'
        content_type = ['text/plain']

    class TestComponentSchema(components.Component):
        id = 'testcomponent'
        schema_title = 'test component'
        content_type = ['text/plain']

        required_text = components.StringSchema(required=True)
        optional_text = components.StringSchema()

        required_attribute = components.Attribute('testattribute',
                                                  required=True)
        optional_attribute = components.Attribute('testattribute')

    def setUp(self):
        self.old_schema_cache = components.ComponentSchemaCache
        components.ComponentSchemaCache = {
            'testcomponent': self.TestComponentSchema,
            'testattribute': self.TestAttributeSchema
        }

    def tearDown(self):
        components.ComponentSchemaCache = self.old_schema_cache

    def _parse_data(self, response):
        try:
            return json.loads(response.content.decode('UTF-8'))
        except ValueError as e:
            self.fail(e)

    def test_valid_component(self):
        url = reverse('component-validity', kwargs={
            'slug': 'valid-component-with-optional-text-optional-attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertIn('valid', data)
        self.assertEqual(data, {'valid': True})

    def test_valid_component_only_required_stuff(self):
        url = reverse('component-validity', kwargs={
            'slug': 'valid-component-only-required-fields'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertIn('valid', data)
        self.assertTrue(data['valid'])

    def test_invalid_component_missing_required_metadata(self):
        url = reverse('component-validity', kwargs={
            'slug': 'invalid-component-missing-required-metadata'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertIn('valid', data)
        self.assertFalse(data['valid'])

    def test_invalid_component_missing_required_attribute(self):
        url = reverse('component-validity', kwargs={
            'slug': 'invalid-component-missing-required-attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertIn('valid', data)
        self.assertFalse(data['valid'])

    def test_invalid_component_invalid_content_type(self):
        url = reverse('component-validity', kwargs={
            'slug': 'invalid-component-invalid-content-type'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertIn('valid', data)
        self.assertFalse(data['valid'])

    def test_invalid_component_missing_schema(self):
        url = reverse('component-validity', kwargs={
            'slug': 'invalid-component-no-such-schema',
        })

        res = self.client.get(url)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertIn('valid', data)
        self.assertFalse(data['valid'])

    def test_get_component_schemas(self):
        url = reverse('component-schemas')

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = self._parse_data(res)
        self.assertEqual(len(data.keys()), 3)
        self.assertIn('testattribute', data)
        self.assertIn('testcomponent', data)
        self.assertIn('id', data)

        jsonschema.validate({}, data)


