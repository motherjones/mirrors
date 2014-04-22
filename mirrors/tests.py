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
from mirrors.views import ComponentDetail
from mirrors.models import *
from mirrors.serializers import *

from mirrors import components


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
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions')
        self.assertEqual(c.binary_data, b'this is the second revision')

    def test_get_binary_data_failure(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')
        self.assertEqual(c.binary_data, None)

    def test_get_data_uri(self):
        expected_url = reverse('component-detail', kwargs={
            'slug': 'test-component-with-no-revisions'
        }) + '/data'

        c = Component.objects.get(slug='test-component-with-no-revisions')
        url = c.data_uri
        self.assertEqual(url, expected_url)

    def test_get_str(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions')
        self.assertEqual(c.__str__(),
                         'test-component-with-multiple-revisions')


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
            c.new_revision(metadata={'title': 'this thing should fail!'})

    def test_new_revision_not_first(self):
        c = Component.objects.get(slug='component-with-binary-data')
        num_orig_components = c.revisions.count()

        cr = c.new_revision(b'this is a new revision', {
            'title': 'test component with no revisions'
        })

        cr = c.revisions.all().order_by('-revision_number').first()
        metadata = cr.metadata
        self.assertEqual(metadata['title'],
                         'test component with no revisions')
        self.assertEqual(cr.revision_number, num_orig_components+1)

    def test_new_revision_no_data(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        with self.assertRaises(ValueError):
            cr = c.new_revision()


class ComponentAttributeTests(MirrorsTestCase):
    fixtures = ['components.json']

    def test_get_attribute(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-levels-sub-1-2')
        c_2 = c.get_attribute('regular_attr')
        self.assertEqual(c_2.slug,
                         'test-component-with-multiple-levels-sub-1')

    def test_get_attribute_list(self):
        c = Component.objects.get(slug='component-with-list-attribute')
        attr_list = c.get_attribute('my_list_attr')

        self.assertEqual(len(attr_list), 3)

    def test_get_attribute_list_one_entry(self):
        c = Component.objects.get(slug='test-component-with-list-one-attribute')
        attr_list = c.get_attribute('my_single_list_attr')

        self.assertTrue(isinstance(attr_list, list))
        self.assertEqual(len(attr_list), 1)

        attr = attr_list[0]
        self.assertEqual(attr.slug, 'attribute-1')

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
        self.assertEqual(ca.weight, -1)
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

    def test_get_str_on_single_attribute(self):
        ca = ComponentAttribute.objects.get(10)
        e_str = 'test-component-with-one-attribute[my_attribute] = attribute-1'
        self.assertEqual(ca.__str__(), e_str)

    def test_get_str_on_list_attribute(self):
        ca = ComponentAttribute.objects.get(7)
        e_str = 'component-with-list-attribute[my_list_attr,500] = attribute-1'
        self.assertEqual(ca.__str__(), e_str)
        


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


class ComponentsTestCase(TestCase):
    def test_attribute_to_dict(self):
        alpha = ['a', 'b', 'c']
        attribute = components.Attribute(*alpha, required=True)
        _dict = dict(attribute)
        for i, c in enumerate(_dict['anyOf']):
            self.assertEqual(c['$ref'], '#%s' % alpha[i])

    def test_list_attribute_to_dict(self):
        alpha = ['a', 'b', 'c']
        attribute = components.AttributeList(*alpha, required=True)
        _dict = dict(attribute)
        self.assertEqual(_dict['type'], 'array')
        self.assertIsInstance(_dict['items']['anyOf'], list)

    def test_metadata(self):
        _dict = {'test': 'test'}
        schema = components.MetaData(_dict=_dict)
        self.assertEqual(schema, _dict)

    def test_string_schema_with_enum(self):
        enum = ['a', 'b', 'c']
        schema = components.StringSchema(enum)
        self.assertEqual(schema['enum'], enum)

    def test_component_with_metadata(self):
        for key in dir(components):
            schema = getattr(components, key)
            if isinstance(schema, type) and \
               issubclass(schema, components.MetaData):
                class Example(components.Component):
                    id = 'example'
                    title = 'Example Component'
                    foo = schema(required=True)

                _dict = dict(Example())
                self.assertEqual(
                    _dict['properties']['metadata']['properties'].get('foo'),
                    dict(schema()))

    def test_component_with_attribute(self):
        class Example(components.Component):
            id = 'example'
            title = 'Example Component'
            foo = components.Attribute('example', required=True)

        _dict = Example()
        foo = _dict['properties']['attributes']['properties'].get('foo')
        required = _dict['properties']['attributes']['required']
        self.assertTrue('foo' in required)  # TODO: Make test both true & false
        self.assertEqual(foo, components.Attribute('example'))

    def test_component_with_attribute_list(self):
        class Example(components.Component):
            id = 'example'
            title = 'Example Component'
            foo = components.AttributeList('example')

        _dict = Example()
        foo = _dict['properties']['attributes']['properties'].get('foo')
        self.assertEqual(foo, components.AttributeList('example'))

    def test_get_components(self):
        comps = components.get_components()
        self.assertTrue(len(comps)>=1)
        for key, comp in comps.items():
            self.assertTrue(issubclass(comp, components.Component))
            self.assertEqual(key, comp.id)

    def test_get_component(self):
        comp = components.get_component('component')
        self.assertTrue(comp, components.Component)

    def test_get_component_fail(self):
        with self.assertRaises(components.MissingComponentException):
            components.get_component('nota valid component')
