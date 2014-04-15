import json
import logging

from rest_framework import serializers
from mirrors.models import Component, ComponentAttribute, ComponentRevision

LOGGER = logging.getLogger(__name__)


class ComponentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    data_uri = serializers.URLField(read_only=True)
    revisions = serializers.RelatedField(many=True, read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')
    metadata = serializers.SerializerMethodField('_get_metadata')

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
            instance.content_type = attrs.get('content_type',
                                              instance.content_type)
            instance.schema_name = attrs.get('schema_name',
                                             instance.schema_name)
            instance.metadata = attrs.get('metadata', instance.metadata)

            return instance

        return Component(**attrs)

    def _get_metadata(self, obj):
        return obj.metadata

    def _get_attributes(self, obj):
        result = {}
        attribute_names = [o.name for o in obj.attributes.distinct('name')]

        for n in attribute_names:
            attr = obj.get_attribute(n)

            if isinstance(attr, list):
                result[n] = [ComponentSerializer(a).data for a in attr]
            else:
                result[n] = ComponentSerializer(attr).data

        return result


class ComponentRevisionSerializer(serializers.ModelSerializer):
    component = serializers.RelatedField(many=False)

    class Meta:
        model = ComponentRevision
        fields = ('revision_date', 'revision_number', 'component')
