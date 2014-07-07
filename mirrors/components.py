class MetaData(dict):
    _default_dict = {}

    def __init__(self, _dict=None, required=None):
        self.required = required
        if _dict:
            self._dict = self._default_dict
        self.update(self._dict)


class StringSchema(MetaData):
    _default_dict = {
        'id': 'stringSchema',
        'type': 'string'
    }

    def __init__(self, enum=None, required=None):
        self._dict = self._default_dict
        if enum:
            self._dict['enum'] = enum
        super(StringSchema, self).__init__(required=required)


class SlugSchema(MetaData):
    _default_dict = {
        'id': 'slugSchema',
        'type': 'string'
    }


class UriSchema(MetaData):
    _default_dict = {
        'id': 'uriSchema',
        'type': 'string'
    }


class EmailSchema(MetaData):
    _default_dict = {
        'id': 'emailSchema',
        'type': 'string'
        }


class Attribute(dict):
    def template(self):
        return {
            'anyOf': [
                {'$ref': '#%s' % c} for c in self.components
            ]
        }

    def __init__(self, *args, required=None):
        self.components = args
        self.required = required
        self.update(self.template())


class AttributeList(Attribute):
    def template(self):
        return {
            'type': 'array',
            'items': super(AttributeList, self).template()
        }


class Component(dict):
    id = 'component'
    schema_title = 'base compononent schema'
    content_type = []

    def __init__(self):
        """
        TODO: Split this up into modules and private/public
        properties.
        """
        required_metadata = []
        metadata = {}
        required_attributes = []
        attributes = {}

        for key in dir(self):
            prop = getattr(self, key)
            if isinstance(prop, MetaData):
                metadata[key] = prop
                if prop.required:
                    required_metadata.append(key)
            elif isinstance(prop, Attribute):
                attributes[key] = prop
                if prop.required:
                    required_attributes.append(key)

        metadata = {
            'type': 'object',
            'properties': metadata,
            'required': required_metadata
        }
        attributes = {
            'type': 'object',
            'properties': attributes,
            'required': required_attributes,
            'additionalProperties': {
                'anyOf': [{'$ref': 'component'}, {
                    'type': 'array',
                    'items': {
                        '$ref': 'component'
                    }
                }]
            }
        }
        schema = {
            'id': '#%s' % self.id,
            'title': self.schema_title,
            'type': 'object',
            'required': ['metadata', 'slug', 'schema_name', 'uri'],
            'properties': {
                'uri': StringSchema(),
                'data_uri': StringSchema(),
                'slug': SlugSchema(),
                'content_type': StringSchema(enum=self.content_type),
                'schema_name': StringSchema(),
                'metadata': metadata,
                'attributes': attributes
            }
        }
        return self.update(schema)


ComponentSchemaCache = {}


class MissingComponentException(Exception):
    pass


def get_components():
    return ComponentSchemaCache


def get_component(_id):
    try:
        return ComponentSchemaCache[_id]
    except KeyError:
        raise MissingComponentException(_id)
