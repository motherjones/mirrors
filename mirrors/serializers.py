import json
import logging

from rest_framework import serializers
from mirrors.models import Component, ComponentAttribute, ComponentRevision

LOGGER = logging.getLogger(__name__)


class ComponentSerializer(serializers.ModelSerializer):
    """A :py:class:Component serializer

    .. todo:: Write real documentation for
              `mirrors.serializer.ComponentSerializer`
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    data_uri = serializers.URLField(read_only=True)
    revisions = serializers.RelatedField(many=True, read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')
    #metadata = serializers.SerializerMethodField('_get_metadata')

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'created_at',
                  'updated_at', 'schema_name', 'revisions', 'data_uri',
                  'attributes')

    def restore_object(self, attrs, instance=None):
        """Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.

        :param attrs: the the key/value pairs (generally made by loading a JSON
                      blob from the client) that represent the fields of a
                      :py:class:`Component` object

        :type attrs: dict
        :param instance: an optional instance of a :py:class:`Component`. If
                         this is set, then the values of `attrs` will be used
                         update it, rather than to create a new
                         :py:class:`Component`.

        :rtype: :py:class:`Component`

        """
        if instance is not None:
            instance.content_type = attrs.get('content_type',
                                              instance.content_type)
            instance.schema_name = attrs.get('schema_name',
                                             instance.schema_name)
            instance.metadata = attrs.get('metadata', instance.metadata)

            return instance

        return Component(**attrs)

    def transform_metadata(self, obj, val):
        """Transform the contents of `metadata` from a string into a dict.

        :param obj: reference to an instance of :py:class:`CompenentSerializer`
        :type obj: :py:class:`CompenentSerializer`
        :param val: the current value of `metadata`
        :type val: str or dict

        :rtype: dict

        """
        if isinstance(val, str):
            return json.loads(val)
        else:
            return val

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
    """A :py:class:ComponentRevision serializer

    .. todo:: Write real documentation for
              `mirrors.serializer.ComponentRevisionSerializer`
    """
    component = serializers.RelatedField(many=False)

    class Meta:
        model = ComponentRevision
        fields = ('revision_date', 'revision_number', 'component')
