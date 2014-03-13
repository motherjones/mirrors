from rest_framework import serializers
from mirrors.models import Component, ComponentRevision


class ChildComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'publish_date',
                  'schema_name', 'members')


class ComponentSerializer(serializers.ModelSerializer):
    attributes = serializers.RelatedField(many=True)
    members = serializers.RelatedField(many=True)
    revisions = serializers.RelatedField(many=True)

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'publish_date',
                  'schema_name', 'members', 'revisions')

ComponentSerializer.base_fields['members'] = ComponentSerializer()


class ComponentRevisionSerializer(serializers.ModelSerializer):
    component = serializers.RelatedField(many=False)

    class Meta:
        model = ComponentRevision
        fields = ('revision_date', 'revision_number', 'component')
