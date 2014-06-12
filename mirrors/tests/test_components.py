from django.test import TestCase

from mirrors import components
from django.test import TestCase


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
        self.assertTrue(len(comps) >= 1)
        for key, comp in comps.items():
            self.assertTrue(issubclass(comp.__class__, components.Component))
            self.assertEqual(key, comp.id)

    def test_get_component(self):
        comp = components.get_component('component')
        self.assertTrue(comp, components.Component)

    def test_get_component_fail(self):
        with self.assertRaises(components.MissingComponentException):
            components.get_component('nota valid component')
