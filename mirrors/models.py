import re
import sys

from django.dispatch import receiver
from django.db import models
from django.db.models import Max
from django.utils import timezone

from jsonfield import JSONField


class Component(models.Model):
    """A component

    .. todo:: Write real documentation for mirrors.Component
    """
    slug = models.SlugField(max_length=100, unique=True)
    metadata = JSONField()
    content_type = models.CharField(max_length=50, default='none')
    publish_date = models.DateTimeField(null=True)
    schema_name = models.CharField(max_length=50, null=True, blank=True)

    @property
    def data_uri(self):
        return "/component/{}/data".format(self.slug)

    @property
    def binary_data(self):
        """Get the data from the most recent revision of the data.

        :rtype: bytes
        """
        rev = self.revisions.order_by('-revision_number').first()

        if rev:
            return rev.data.tobytes()
        else:
            return None

    def new_revision(self, data=None, metadata=None):
        """Create a new revision for this :py:class:`Component` object. If the
        data is not in the correct format it will attempt to convert it into a
        bytes object.

        Passing None for one of the arguments will result in that data not
        being changed.

        :param data: the actual content of the new revision
        :type data: `bytes`
        :param metadata: the new metadata
        :type metadata: `dict`

        :rtype: :py:class:`ComponentRevision`
        :raises: `ValueError`
        """
        if not data and not metadata:
            raise ValueError('no new data was actually provided')

        cur_rev = self.revisions.all().order_by('-revision_number').first()
        if not cur_rev:
            cur_rev_num = 0
            new_data = None
            new_metadata = self.metadata

            if not data:
                raise ValueError(
                    'both metadata and data must be provided for 1st revision'
                )
        else:
            cur_rev_num = cur_rev.revision_number
            new_data = cur_rev.data
            new_metadata = cur_rev.metadata

        if data:
            new_data = data
        if metadata:
            new_metadata = metadata

        new_rev = ComponentRevision.objects.create(
            revision_number=cur_rev_num+1,
            data=data,
            diff=None,  # figure this out later
            metadata=metadata,
            revision_date=timezone.now(),
            component=self
        )

        return new_rev

    def new_attribute(self, name, child, weight=9999):
        """Add a new named attribute to the :py:class:`Component` object. This
        will overwrite an attribute if the child is unchanged. However, if the
        child has a different slug, then the attribute will be converted into
        an ordered list and the child component added to it.
        :param name: the attribute's name, which can only contain alphanumeric
                     characters as well as the - and _ characters.
        :type name: string
        :param child: the `Component` object to associate with that name
        :type child: `Component`
        :param weight: the weight of the child within the ordered list, if the
                       attribue is one
        :type weight: int

        :rtype: :py:class:`ComponentAttribute` or a list

        """

        if not child or child == self:
            raise ValueError('child cannot be None or self')

        if not re.match('^\w[-\w]*$', name):
            raise KeyError('invalid attribute name')

        if self.attributes.filter(name=name).count() == 1:
            attr = self.attributes.get(name=name)

        new_attr = ComponentAttribute(
            name=name,
            parent=self,
            child=child,
            weight=weight
        ).save()

        return new_attr

    def get_attribute(self, attribute_name):
        """Retrieve the `Component` object attached to this one by the
        attribute name if it is a regular attribute, or a list if it contains
        more than one

        :param attribute_name: name of the attribute
        :type attribute_name: str
        :rtype: `Component` or list
        """
        attrs = self.attributes.filter(name=attribute_name)

        if attrs.count() == 0:
            raise KeyError("no such attribute '{}'".format(attribute_name))
        elif attrs.count() == 1:
            return attrs.first().child
        elif attrs.count() > 1:
            return [attr.child for attr in attrs.order_by('weight')]


class ComponentAttribute(models.Model):
    """Named attributes that associate :py:class:`Component` objects with
    other `Component` objects.
    """
    parent = models.ForeignKey('Component', related_name='attributes')
    child = models.ForeignKey('Component')
    name = models.CharField(max_length=255)
    weight = models.IntegerField(null=False, default=-1)

    added_time = models.DateTimeField(auto_now_add=True)


class ComponentRevision(models.Model):
    """A revision of the data contained by a :py:class:Component object.

    .. todo:: Write real documentation for mirrors.ComponentRevision
    """
    data = models.BinaryField()
    diff = models.BinaryField(null=True, blank=True)
    metadata = JSONField()

    revision_date = models.DateTimeField(auto_now_add=True)
    revision_number = models.IntegerField(default=1)

    component = models.ForeignKey('Component', related_name='revisions')
