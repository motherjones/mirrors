import json

from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TestCase, Client

from mirrors.models import *


class ComponentModelTests(TestCase):
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

    def test_get_unset_metadata(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')
        self.assertEqual(c.metadata, {})

    def test_get_str(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions')
        self.assertEqual(c.__str__(),
                         'test-component-with-multiple-revisions')


class ComponentRevisionModelTests(TestCase):
    fixtures = ['components.json']

    def test_new_revision_first(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        c.new_revision(data=b'this is a new revision', metadata=json.dumps({
            'title': 'test component with no revisions'
        }))

        cr = c.revisions.order_by('-created_at').first()

        self.assertEqual(c.revisions.count(), 1)
        self.assertEqual(cr.component, c)
        self.assertEqual(bytes(cr.data), b'this is a new revision')

    def test_new_revision_no_data(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        with self.assertRaises(ValueError):
            cr = c.new_revision()

    def test_new_revision_no_metadata(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')

        c.new_revision(data=b'this is test data')
        self.assertEqual(c.metadata, {})

    def test_revision_to_str(self):
        c = Component.objects.filter(
            slug='test-component-with-multiple-revisions'
        ).first()
        cr = c.revisions.first()

        self.assertEqual(cr.__str__(),
                         'test-component-with-multiple-revisions v1')


class ComponentAttributeModelTests(TestCase):
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
        c = Component.objects.get(slug='test-component-with-list'
                                       '-one-attribute')
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
        ca = ComponentAttribute.objects.get(pk=10)
        e_str = 'test-component-with-one-attribute[my_attribute] = attribute-1'
        self.assertEqual(ca.__str__(), e_str)

    def test_get_str_on_list_attribute(self):
        ca = ComponentAttribute.objects.get(pk=7)
        e_str = ('component-with-list-attribute[my_list_attr,500] '
                 '-> attribute-1')
        self.assertEqual(ca.__str__(), e_str)
