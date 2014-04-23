import json
import hashlib

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIClient

from mirrors.models import *
from mirrors.serializers import *


class ComponentResourceTests(APITestCase):
    fixtures = ['serializer.json']

    def _has_attribute(self, content, name):
        return name in content['attributes'].keys()

    def _get_attribute(self, content, name):
        return content['attributes'][name]

    def test_serialize_component_resource(self):
        c = Component.objects.get(slug='test-component-with-no-attributes')
        content = ComponentSerializer(c).data

        expected_url = reverse('component-detail', kwargs={
            'slug': 'test-component-with-no-attributes'
        }) + '/data'

        self.assertEqual(content['slug'], 'test-component-with-no-attributes')
        self.assertEqual(content['data_uri'], expected_url)
        self.assertEqual(content['content_type'], 'application/x-markdown')
        self.assertEqual(content['schema_name'], 'article')
        self.assertEqual(content['metadata'], {
            "title": "test component with no attributes",
            "description": "this is a test article"
        })

    def test_serialize_component_with_attribute(self):
        c = Component.objects.get(
            slug='test-component-with-one-named-attribute')
        content = ComponentSerializer(c).data

        self.assertEqual(content['slug'],
                         'test-component-with-one-named-attribute')
        self.assertIn('attributes', content)
        self.assertTrue(self._has_attribute(content, 'my_named_attribute'))

        attribute = self._get_attribute(content, 'my_named_attribute')
        self.assertTrue(isinstance(attribute, dict))

    def test_serialize_component_with_attribute_list(self):
        c = Component.objects.get(slug='test-component-with-list-attribute')
        content = ComponentSerializer(c).data

        self.assertEqual(content['slug'], 'test-component-with-list-attribute')
        self.assertTrue(self._has_attribute(content, 'my_list_attribute'))

        attribute = self._get_attribute(content, 'my_list_attribute')

        self.assertTrue(isinstance(attribute, list))
        self.assertEqual(len(attribute), 3)

        found_slugs = [x['slug'] for x in attribute]
        expected_slugs = ['attribute-4', 'attribute-3', 'attribute-1']

        for e in zip(found_slugs, expected_slugs):
            self.assertEqual(e[0], e[1])

    def test_serialize_component_with_mixed_attributes(self):
        c = Component.objects.get(slug='test-component-mixed-attributes')
        content = ComponentSerializer(c).data

        self.assertEqual(content['slug'], 'test-component-mixed-attributes')
        self.assertTrue(self._has_attribute(content, 'my_list_attribute'))
        self.assertTrue(self._has_attribute(content, 'my_attribute'))

        list_attr = self._get_attribute(content, 'my_list_attribute')
        named_attr = self._get_attribute(content, 'my_attribute')

        self.assertTrue(isinstance(list_attr, list))
        self.assertEqual(len(list_attr), 2)

    def test_transform_metadata_from_string(self):
        c = Component.objects.get(slug='test-component-mixed-attributes')
        serializer = ComponentSerializer(c)
        metadata_str = json.dumps({'test': 'value'})

        result = serializer.transform_metadata(None, metadata_str)
        self.assertEqual(result, {'test': 'value'})

    def test_transform_metadata_from_dict(self):
        c = Component.objects.get(slug='test-component-mixed-attributes')
        serializer = ComponentSerializer(c)
        metadata_dict = {'test': 'value'}

        result = serializer.transform_metadata(None, metadata_dict)
        self.assertEqual(result, {'test': 'value'})
