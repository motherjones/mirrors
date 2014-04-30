import json

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from mirrors.views import ComponentDetail


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


class ComponentAttributeViewTests(APITestCase):
    fixtures = ['users.json', 'componentattributes.json']

    def test_get_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-regular-attribute',
            'attr_name': 'my_attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('child', data)
        self.assertEqual(data['child'], 'attribute-1')

    def test_get_404_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-regular-attribute',
            'attr_name': 'no_such_attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_new_attribute(self):
        url = reverse('component-attribute-list', kwargs={
            'component': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': 'new_attribute',
                                     'child': 'attribute-4'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertIn('child', data)
        self.assertNotIn('weight', data['child'])
        self.assertEqual(data['child'], 'attribute-4')

    def test_post_new_attribute_invalid_name(self):
        url = reverse('component-attribute-list', kwargs={
            'component': 'component-with-regular-attribute'
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
            'component': 'component-with-regular-attribute'
        })

        res = self.client.post(url, {'name': 'my_attribute',
                                     'child': 'attribute-4'})

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_post_new_attribute_invalid_component_name(self):
        url = reverse('component-attribute-list', kwargs={
            'component': 'component-with-regular-attribute'
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
            'component': 'component-with-regular-attribute'
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
            'component': 'component-with-list-attribute',
            'attr_name': 'list_attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        print("data: {}".format(data))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['child'], 'attribute-3')
        self.assertEqual(data[1]['child'], 'attribute-4')

        self.assertEqual(data[0]['weight'], 100)
        self.assertEqual(data[1]['weight'], 200)

    def test_get_404_attribute_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'no-such-attribute'
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_new_attribute_to_existing_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'list_attribute'
        })

        new_attribute = {'child': 'attribute-1', 'weight': 9999}

        res = self.client.post(url, data=new_attribute)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0]['child'], 'attribute-3')
        self.assertEqual(data[1]['child'], 'attribute-4')
        self.assertEqual(data[2]['child'], 'attribute-1')

        self.assertEqual(data[0]['weight'], 100)
        self.assertEqual(data[1]['weight'], 200)
        self.assertEqual(data[2]['weight'], 9999)

    def test_patch_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-regular-attribute',
            'attr_name': 'my_attribute'
        })
        patch_data = {'child': 'attribute-4'}

        res = self.client.patch(url, patch_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data['child'], 'attribute-4')

    def test_patch_list_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'list_attribute',
            'index': 1
        })
        patch_data = {'weight': 10000}

        res = self.client.patch(url, patch_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['child'], 'attribute-4')
        self.assertEqual(data[1]['child'], 'attribute-3')

        self.assertEqual(data[0]['weight'], 200)
        self.assertEqual(data[1]['weight'], 10000)

    def test_patch_404_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'no-such-attribute'
        })
        patch_data = {'weight': 10000}

        res = self.client.patch(url, patch_data)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-regular-attribute',
            'attr_name': 'my_attribute'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_404_attribute(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-regular-attribute',
            'attr_name': 'no-such-slug'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_attribute_list(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'list_attribute'
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_attribute_list_element(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'list_attribute',
            'index': 1
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = json.loads(res.content.decode('UTF-8'))
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['child'], 'attribute-3')
        self.assertEqual(data[0]['weight'], 100)

    def test_delete_attribute_list_404_element(self):
        url = reverse('component-attribute-detail', kwargs={
            'component': 'component-with-list-attribute',
            'attr_name': 'list_attribute',
            'index': 9999
        })

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
