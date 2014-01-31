from rest_framework import serializers
from mirrors.models import Content, ContentRevision


class ChildContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ('slug', 'metadata', 'content_type', 'publish_date',
                  'schema_name', 'members')


class ContentSerializer(serializers.ModelSerializer):
    attributes = serializers.RelatedField(many=True)
    members = serializers.RelatedField(many=True)
    revisions = serializers.RelatedField(many=True)

    class Meta:
        model = Content
        fields = ('slug', 'metadata', 'content_type', 'publish_date',
                  'schema_name', 'members', 'revisions')

ContentSerializer.base_fields['members'] = ContentSerializer()


class ContentRevisionSerializer(serializers.ModelSerializer):
    content = serializers.RelatedField(many=False)

    class Meta:
        model = ContentRevision
        fields = ('revision_date', 'revision_number', 'content')
