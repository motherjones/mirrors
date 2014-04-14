import json
import logging

from rest_framework import serializers
from mirrors.models import Component, ComponentAttribute, ComponentRevision

LOGGER = logging.getLogger(__name__)


class ComponentSerializer(serializers.ModelSerializer):
    #slug = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    metadata = serializers.CharField(required=False)
    data_uri = serializers.URLField(read_only=True)
    revisions = serializers.RelatedField(many=True, read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'created_at',
                  'updated_at', 'schema_name', 'revisions', 'data_uri',
                  'attributes')

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.content_type = attrs.get('content_type', instance.content_type)
            instance.schema_name = attrs.get('schema_name', instance.schema_name)
            instance.metadata = attrs.get('metadata', instance.metadata)
            
            return instance

        return Component(**attrs)

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

    # def transform_metadata(self, obj, value):
    #     if isinstance(value, str):
    #         LOGGER.error('transform: type={}, value {}'.format(value.__class__,value))
    #         return json.loads(value)
    #     return value


class ComponentRevisionSerializer(serializers.ModelSerializer):
    component = serializers.RelatedField(many=False)

    class Meta:
        model = ComponentRevision
        fields = ('revision_date', 'revision_number', 'component')
