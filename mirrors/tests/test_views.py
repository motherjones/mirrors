import hashlib
import json
import os

from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory

from rest_framework import status
from rest_framework.test import APITestCase

from mirrors.models import Component, ComponentRevision
from mirrors.views import ComponentData as ComponentDataView


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
        data = json.loads(data['metadata'])
        self.assertEqual(data['title'], 'Valid component')

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
                         data={'file': upload_file},
                         content_type='multipart/form-data')

            self.assertTrue(res.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(component.revisions.count(), 1)

            rev = component.revisions.first()
            md5_hash = hashlib.md5()
            md5_hash.update(rev.data)
            self.assertEqual(md5_hash.hexdigest(), self.md_hash)
