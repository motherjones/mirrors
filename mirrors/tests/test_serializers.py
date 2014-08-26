import json

import jsonschema

from django.core.urlresolvers import reverse

from rest_framework import serializers
from rest_framework.test import APITestCase

from mirrors.models import Component
from mirrors.models import ComponentAttribute
from mirrors.models import ComponentRevision
from mirrors.serializers import ComponentSerializer
from mirrors.serializers import ComponentWithDataSerializer
from mirrors.serializers import ComponentAttributeSerializer
from mirrors.serializers import ComponentRevisionSerializer


class ComponentResourceTests(APITestCase):
    fixtures = ['serializer.json']

    def _has_attribute(self, content, name):
        return name in content['attributes'].keys()

    def _get_attribute(self, content, name):
        return content['attributes'][name]

    def test_serialize_component_resource(self):
        c = Component.objects.get(slug='test-component-with-no-attributes',
                                  year=2014,
                                  month=2)
        content = ComponentSerializer(c).data

        self.assertTrue(isinstance(content, dict))
        self.assertEqual(set(content.keys()), {'slug',
                                               'year',
                                               'month',
                                               'content_type',
                                               'schema_name',
                                               'metadata',
                                               'attributes',
                                               'created_at',
                                               'revisions',
                                               'updated_at'})

        self.assertEqual(content['slug'], 'test-component-with-no-attributes')
        self.assertEqual(content['year'], 2014)
        self.assertEqual(content['month'], 2)
        self.assertEqual(content['content_type'], 'application/x-markdown')
        self.assertEqual(content['schema_name'], 'article')
        self.assertEqual(content['metadata'], {
            "title": "test component with no attributes",
            "description": "this is a test article"
        })

    def test_serialize_component_with_attribute(self):
        c = Component.objects.get(
            slug='test-component-with-one-named-attribute',
            year=2014,
            month=2
        )
        content = ComponentWithDataSerializer(c).data

        self.assertEqual(content['slug'],
                         'test-component-with-one-named-attribute')
        self.assertIn('attributes', content)
        self.assertTrue(self._has_attribute(content, 'my_named_attribute'))

        attribute = self._get_attribute(content, 'my_named_attribute')
        self.assertTrue(isinstance(attribute, dict))

    def test_serialize_component_with_attribute_list(self):
        c = Component.objects.get(slug='test-component-with-list-attribute',
                                  year=2014,
                                  month=2)
        content = ComponentWithDataSerializer(c).data

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
        c = Component.objects.get(slug='test-component-mixed-attributes',
                                  year=2014,
                                  month=2)
        content = ComponentWithDataSerializer(c).data

        self.assertEqual(content['slug'], 'test-component-mixed-attributes')
        self.assertTrue(self._has_attribute(content, 'my_list_attribute'))
        self.assertTrue(self._has_attribute(content, 'my_attribute'))

        list_attr = self._get_attribute(content, 'my_list_attribute')
        named_attr = self._get_attribute(content, 'my_attribute')

        self.assertTrue(isinstance(list_attr, list))
        self.assertEqual(len(list_attr), 2)

    def test_transform_metadata_from_string(self):
        c = Component.objects.get(slug='test-component-mixed-attributes',
                                  year=2014,
                                  month=2)
        serializer = ComponentWithDataSerializer(c)
        metadata_str = json.dumps({'test': 'value'})

        result = serializer.transform_metadata(serializer, metadata_str)
        self.assertEqual(result, {'test': 'value'})

    def test_transform_metadata_from_dict(self):
        c = Component.objects.get(slug='test-component-mixed-attributes',
                                  year=2014,
                                  month=2)
        serializer = ComponentWithDataSerializer(c)
        metadata_dict = {'test': 'value'}

        result = serializer.transform_metadata(None, metadata_dict)
        self.assertEqual(result, {'test': 'value'})

    def test_validate_non_string_or_dict_metadata(self):
        c = Component.objects.get(slug='test-component-mixed-attributes',
                                  year=2014,
                                  month=2)
        serializer = ComponentWithDataSerializer(c)

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_metadata({'metadata': 32}, 'metadata')


class ComponentAttributeResourceTests(APITestCase):
    fixtures = ['users.json', 'componentattributes.json']

    def test_serialize_single_attribute(self):
        parent = Component.objects.filter(
            slug='component-with-regular-attribute',
            year=2014,
            month=4
        ).first()

        ca = ComponentAttribute.objects.filter(parent=parent).first()
        content = ComponentAttributeSerializer(ca).data

        self.assertIn('name', content)
        self.assertIn('child', content)

        self.assertEqual(content['child'], 'attribute-1')
        self.assertEqual(content['name'], 'my_attribute')

    def test_serialize_list_attribute(self):
        cas = ComponentAttribute.objects.filter(
            name='list_attribute').order_by('weight')
        content = ComponentAttributeSerializer(cas).data

        self.assertTrue(isinstance(content, list))
        self.assertEqual(len(content), 2)

        attr_1 = content[0]
        attr_2 = content[1]

        self.assertEqual(attr_1['child'], 'attribute-3')
        self.assertEqual(attr_1['weight'], 100)

        self.assertEqual(attr_2['child'], 'attribute-4')
        self.assertEqual(attr_2['weight'], 200)


class ComponentRevisionResourceTests(APITestCase):
    fixtures = ['users.json', 'componentrevisions.json']

    def test_serialize_revision_with_multiple_type_changes(self):
        c_rev = ComponentRevision.objects.get(pk=4)
        rev = ComponentRevisionSerializer(c_rev).data

        self.assertTrue(isinstance(rev, dict))
        self.assertEqual(rev['version'], 1)
        self.assertEqual(str(rev['change_date']),
                         '2014-06-09 19:50:40.797000+00:00')

        self.assertTrue(isinstance(rev['change_types'], list))
        self.assertEqual(len(rev['change_types']), 2)
        self.assertIn('data', rev['change_types'])
        self.assertIn('metadata', rev['change_types'])

    def test_serialize_revision_summary(self):
        rev_1 = ComponentRevisionSerializer(
            ComponentRevision.objects.get(pk=3)
        ).data
        rev_2 = ComponentRevisionSerializer(
            ComponentRevision.objects.get(pk=5)
        ).data

        self.assertTrue(isinstance(rev_1, dict))
        self.assertEqual(rev_1['version'], 1)
        self.assertEqual(str(rev_1['change_date']),
                         '2014-06-09 19:44:12.459000+00:00')
        self.assertEqual(rev_1['change_types'], ['metadata'])

        self.assertEqual(rev_2['version'], 2)
        self.assertEqual(str(rev_2['change_date']),
                         '2014-06-09 19:56:42.455000+00:00')
        self.assertEqual(rev_2['change_types'], ['data'])
