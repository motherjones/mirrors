import json
from rest_framework import serializers
from mirrors.models import Component, ComponentAttribute, ComponentRevision


class ComponentSerializer(serializers.ModelSerializer):
    revisions = serializers.RelatedField(many=True)
    data_uri = serializers.URLField(read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')
    metadata = serializers.SerializerMethodField('_get_metadata')

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'publish_date',
                  'schema_name', 'revisions', 'data_uri', 'attributes')

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
