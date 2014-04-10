import json

from rest_framework import serializers
from mirrors.models import Component, ComponentAttribute, ComponentRevision


class ComponentSerializer(serializers.ModelSerializer):
    revisions = serializers.RelatedField(many=True)
    data_uri = serializers.URLField(read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'created_at',
                  'updated_at', 'schema_name', 'revisions', 'data_uri',
                  'attributes')

    def _get_attributes(self, obj):
        result = []
        attribute_names = [o.name for o in obj.attributes.distinct('name')]

        for n in attribute_names:
            attr = obj.get_attribute(n)

            if isinstance(attr, list):
                result.append({
                    'name': n,
                    'value': [ComponentSerializer(a).data for a in attr]
                })
            else:
                result.append({'name': n,
                               'value': ComponentSerializer(attr).data})

        return result

    def transform_metadata(self, obj, value):
        if isinstance(value, str):
            return json.loads(value)
        elif isinstance(value, dict):
            return value
        else:
            raise ValueError()


class ComponentRevisionSerializer(serializers.ModelSerializer):
    component = serializers.RelatedField(many=False)

    class Meta:
        model = ComponentRevision
        fields = ('revision_date', 'revision_number', 'component')
