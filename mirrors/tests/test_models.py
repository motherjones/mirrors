import datetime
import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from mirrors.exceptions import LockEnforcementError
from mirrors.models import Component
from mirrors.models import ComponentLock
from mirrors.models import ComponentAttribute


class ComponentModelTests(TestCase):
    fixtures = ['components.json']

    def test_get_binary_data(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions')
        self.assertEqual(c.binary_data, b'this is the second revision')

    def test_get_binary_data_failure(self):
        c = Component.objects.get(slug='test-component-with-no-revisions')
        self.assertEqual(c.binary_data, None)

    def test_get_nonexisttant_data_uri(self):
        c = Component.objects.get(slug='test-component-1')
        self.assertIsNone(c.data_uri)

    def test_get_data_uri(self):
        expected_url = reverse('component-detail', kwargs={
            'slug': 'component-with-binary-data'
        }) + '/data'

        c = Component.objects.get(slug='component-with-binary-data')
        self.assertEqual(c.data_uri, expected_url)

    def test_get_str(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions')
        self.assertEqual(c.__str__(),
                         'test-component-with-multiple-revisions')

    def test_get_metadata(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions'
        )

        expected_metadata = {
            "title": "component data that has multiple revisions",
            "author": "bobby tables"
        }
        self.assertEqual(c.metadata, expected_metadata)

    def test_get_missing_metadata(self):
        c = Component.objects.get(
            slug='test-component-with-no-metadata'
        )

        self.assertEqual(c.metadata, {})

    def test_get_metadata_missing_version(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions'
        )

        with self.assertRaises(IndexError):
            c.metadata_at_version(999)

    def test_get_binary_data_missing_version(self):
        c = Component.objects.get(
            slug='test-component-with-multiple-revisions'
        )

        with self.assertRaises(IndexError):
            c.binary_data_at_version(999)

    def test_get_binary_data_no_data(self):
        c = Component.objects.get(
            slug='test-component-with-no-data'
        )

        self.assertIs(c.binary_data_at_version(1), None)


class ComponentLockTests(TestCase):
    fixtures = ['users.json', 'component_lock_data.json']

    def setUp(self):
        self.test_user = User.objects.get(username='test_user')
        self.test_staff = User.objects.get(username='test_staff')

    def test_lock_component(self):
        c = Component.objects.get(slug='unlocked-component')
        c.lock_by(self.test_user)

        cl = c.lock
        t_delta = datetime.timedelta(hours=1)
        expected_end_date = cl.locked_at + t_delta

        self.assertIsNot(cl, None)
        self.assertTrue(isinstance(cl, ComponentLock))
        self.assertEqual(cl.locked_by, self.test_user)

        self.assertEqual(cl.lock_ends_at.strftime("%Y-%m-%d %H:%M:%S"),
                         expected_end_date.strftime("%Y-%m-%d %H:%M:%S"))

    def test_lock_locked_component(self):
        c = Component.objects.get(slug='locked-component')

        with self.assertRaises(LockEnforcementError):
            c.lock_by(self.test_staff)

    def test_extend_lock(self):
        c = Component.objects.get(slug='locked-component')

        cur_end = c.lock.lock_ends_at
        new_end = cur_end + datetime.timedelta(hours=1)

        c.lock.extend_lock(hours=1)

        self.assertEqual(c.lock.lock_ends_at, new_end)

    def test_unlock_component(self):
        c = Component.objects.get(slug='locked-component')
        c.unlock(self.test_user)

        self.assertIs(c.lock, None)


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
            c.new_revision()

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
            c.get_attribute('no-such-attribute')

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
