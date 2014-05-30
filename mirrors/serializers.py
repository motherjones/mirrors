import json
import logging

from rest_framework import serializers
from mirrors.models import Component, ComponentAttribute, ComponentRevision

LOGGER = logging.getLogger(__name__)


class ComponentSerializer(serializers.ModelSerializer):
    """Used for turning a JSON blob into a :class:`mirrors.models.Component`
    object, and back again.

    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    data_uri = serializers.URLField(read_only=True)
    revisions = serializers.RelatedField(many=True, read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')
    metadata = serializers.CharField(read_only=True)

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'created_at',
                  'updated_at', 'schema_name', 'revisions', 'data_uri',
                  'attributes')

    def restore_object(self, attrs, instance=None):
        """Given a dictionary of deserialized field values, either update an existing
        model instance, or create a new model instance.

        :param attrs: the the key/value pairs (generally made by loading a JSON
                      blob from the client) that represent the fields of a
                      ``Component`` object
        :type attrs: dict

        :param instance: an optional instance of a ``Component``. If this is
                         set, then the values of `attrs` will be used update
                         it, rather than to create a new ``Component``.
        :type instance: :class:`mirrors.models.Component`
        :rtype: :class:`mirrors.models.Component`

        """
        if instance is not None:
            instance.content_type = attrs.get('content_type',
                                              instance.content_type)
            instance.schema_name = attrs.get('schema_name',
                                             instance.schema_name)

            return instance

        return Component(**attrs)

    def transform_metadata(self, obj, val):
        """Transform the contents of `metadata` from a string into a dict.

        :param obj: reference to an instance of ``CompenentSerializer``
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


class ComponentAttributeSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(slug_field='slug')
    child = serializers.SlugRelatedField(slug_field='slug')
    weight = serializers.IntegerField(required=False)
    name = serializers.SlugField()

    class Meta:
        model = ComponentAttribute
        fields = ('parent', 'child', 'weight', 'name')


class ComponentRevisionSerializer(serializers.ModelSerializer):
    """Used for turning a JSON blob into a
     :class:`mirrors.models.ComponentRevision` and back again.

    """
    component = serializers.RelatedField(many=False)

    class Meta:
        model = ComponentRevision
        fields = ('revision_date', 'revision_number', 'component')
