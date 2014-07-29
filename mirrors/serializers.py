import json
import logging

from rest_framework import serializers
from mirrors.models import *

LOGGER = logging.getLogger(__name__)


class WritableSerializerMethodField(serializers.SerializerMethodField):
    """A field that gets and sets its value by calling a method on the serializer
    it's attached to.
    """

    def __init__(self, get_method_name, set_method_name, *args, **kwargs):
        self.read_only = False
        self.get_method_name = get_method_name
        self.method_name = get_method_name
        self.set_method_name = set_method_name

        super(WritableSerializerMethodField, self).__init__(get_method_name,
                                                            *args,
                                                            **kwargs)

    def field_from_native(self, data, files, field_name, into):
        return getattr(self.parent, self.set_method_name)(data,
                                                          files,
                                                          field_name,
                                                          into)


class ComponentSerializer(serializers.ModelSerializer):
    """Used for turning a JSON blob into a :class:`mirrors.models.Component`
    object, and back again.

    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    data_uri = serializers.URLField(read_only=True)
    revisions = serializers.RelatedField(many=True, read_only=True)
    attributes = serializers.SerializerMethodField('_get_attributes')
    metadata = WritableSerializerMethodField('_get_metadata',
                                             '_set_metadata')

    _version = None
    # this is used to store the metadata that gets submitted as part of the
    # post process so that we can save it the correct way by overriding
    _metadata = None

    class Meta:
        model = Component
        fields = ('slug', 'metadata', 'content_type', 'created_at',
                  'updated_at', 'schema_name', 'revisions', 'data_uri',
                  'attributes')

    def __init__(self, *args, **kwargs):
        self._version = kwargs.pop('version', None)
        super(ComponentSerializer, self).__init__(*args, **kwargs)

    def save_object(self, obj, **kwargs):
        """Save the data in this object to the database, including any metadata
        that may have been passed to it through ``__init__()``.

        :param obj: the object we want to commit to the database
        :type obj: :class:`ComponentSerializer`
        """
        super(ComponentSerializer, self).save_object(obj, **kwargs)

        if self._metadata is not None:
            self.object.new_revision(metadata=self._metadata)
            self._metadata = None

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

    def _get_metadata(self, obj):
        if self._version is not None:
            return obj.metadata_at_version(self._version)
        else:
            return obj.metadata

    def _set_metadata(self, data, *args, **kwargs):
        if 'metadata' in data:
            self.validate_metadata(data, 'metadata')
            self._metadata = data['metadata']

    def validate_metadata(self, attrs, source):
        if source not in attrs:
            return attrs

        if not isinstance(attrs[source], dict):
            try:
                attrs[source] = json.loads(attrs[source])
            except Exception:
                raise serializers.ValidationError("This field must be a JSON "
                                                  "object")

        return attrs

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
    version = serializers.IntegerField(read_only=True)
    change_date = serializers.DateTimeField(read_only=True,
                                            source='created_at')
    change_types = serializers.SerializerMethodField('_get_change_types')

    class Meta:
        model = ComponentRevision
        fields = ('version', 'change_date', 'change_types')

    def _get_change_types(self, obj):
        changes = []

        if obj.data is not None:
            changes.append('data')

        if obj.metadata is not None:
            changes.append('metadata')

        return changes


class ComponentLockSerializer(serializers.ModelSerializer):
    locked = serializers.SerializerMethodField('return_true')
    locked_by = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = ComponentLock
        fields = ('locked', 'locked_by', 'locked_at', 'lock_ends_at',)

    def return_true(self, obj):
        return True
