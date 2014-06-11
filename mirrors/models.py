import re
import sys

from django.dispatch import receiver
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.core.urlresolvers import reverse

from jsonfield import JSONField


class Component(models.Model):
    """A ``Component`` is the basic type of object for all things in the Mirrors
    content repository. Anything that has a presence in the final output of the
    website is made of at least one ``Component`` object, and will generally be
    made from several few.

    .. warning :: The implementation of this class is incomplete and may change
                  in the future.

    """
    slug = models.SlugField(max_length=100, unique=True)
    content_type = models.CharField(max_length=50, default='none')
    schema_name = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def data_uri(self):
        """Get the URI for this ``Component``.

        :rtype: str
        """
        return reverse('component-data', kwargs={'slug': self.slug})

    @property
    def metadata(self):
        """Get the current metadata from the most recent revision of the
        component.

        :rtype: dict
        """
        return self.metadata_at_version(self.max_version)

    @property
    def binary_data(self):
        """Get the data from the most recent revision of the data.

        :rtype: bytes
        """
        try:
            return self.binary_data_at_version(self.max_version)
        except IndexError:
            return None

    @property
    def max_version(self):
        """Get the version number for the most recent revision.

        :rtype: int

        .. note :: If there are no revisions, max_version will be 0
        """
        version = self.revisions.all().aggregate(Max('version'))
        if version['version__max'] is None:
            return 0
        else:
            return version['version__max']

    def _version_in_range(self, version):
        return (version > 0) and (version <= self.max_version)

    def new_revision(self, data=None, metadata=None):
        """Create a new revision for this ``Component`` object. If the data is not in
        the correct format it will attempt to convert it into a bytes object.

        Passing None for one of the arguments will result in that data not
        being changed.

        :param data: the actual content of the new revision
        :type data: bytes
        :param metadata: the new metadata
        :type metadata: dict

        :rtype: :class:`ComponentRevision`
        :raises: :class:`ValueError`

        """
        if not data and not metadata:
            raise ValueError('no new revision data was actually provided')

        next_version = 1
        cur_rev = self.revisions.all().order_by('-version').first()
        if cur_rev is not None:
            next_version = cur_rev.version + 1

        new_rev = ComponentRevision.objects.create(
            data=data,
            metadata=metadata,
            component=self,
            version=next_version
        )
        new_rev.save()

        return new_rev

    def new_attribute(self, name, child, weight=-1):
        """Add a new named attribute to the ``Component`` object. This will overwrite
        an attribute if the child is unchanged. However, if the child has a
        different slug, then the attribute will be converted into an ordered
        list and the child component added to it.

        :param name: the attribute's name, which can only contain alphanumeric
                     characters as well as the - and _ characters.

        :type name: str
        :param child: the `Component` object to associate with that name
        :type child: `Component`
        :param weight: the weight of the child within the ordered list, if the
                       attribute is one
        :type weight: int

        :rtype: :class:`ComponentAttribute` or a list

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
            attr = attrs.first()
            if attr.weight == -1:
                return attr.child
            else:
                return [attr.child]
        elif attrs.count() > 1:
            return [attr.child for attr in attrs.order_by('weight')]

    def metadata_at_version(self, version):
        """Get the metadata for the :class:`Component` as it was at the
        provided version.

        :param version: The version of the `Component` that you want to get
                        the metadata for.
        :type version: int

        :rtype: dict
        :raises: :class:`IndexError`
        """
        if not self._version_in_range(version):
            raise IndexError('No such version')

        qs = self.revisions.filter(metadata__isnull=False,
                                   version__lte=version).order_by('-version')
        rev = qs.first()

        if rev is not None:
            return rev.metadata
        else:
            return None

    def binary_data_at_version(self, version):
        """Get the binary data for the :class:`Component` as it was at the
        provided version.

        :param version: The version of the `Component` that you want to get
                        the binary data for.
        :type version: int

        :rtype: bytes
        :raises: :class:`IndexError`
        """

        if not self._version_in_range(version):
            raise IndexError('No such version')

        qs = self.revisions.filter(data__isnull=False,
                                   version__lte=version).order_by('-version')
        rev = qs.first()

        if rev is not None:
            return rev.data
        else:
            return None

    def __str__(self):
        return self.slug


class ComponentAttribute(models.Model):
    """A named connection between a :class:`Component` and one or more other
    ``Component`` objects that are considered to be attributes of the
    first. Some examples of that might include an attribute named "author" that
    connects an article ``Component`` to the ``Component`` that contains
    information about its author.

    .. warning :: The implementation of this class is incomplete and may change
                  in the future.

    """
    parent = models.ForeignKey('Component', related_name='attributes')
    child = models.ForeignKey('Component')
    name = models.CharField(max_length=255)
    weight = models.IntegerField(null=False, default=-1)

    added_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.weight != -1:
            return "{}[{},{}] -> {}".format(self.parent.slug,
                                            self.name,
                                            self.weight,
                                            self.child.slug)
        else:
            return "{}[{}] = {}".format(self.parent.slug,
                                        self.name,
                                        self.child.slug)


class ComponentRevision(models.Model):
    """A revision of the data and metadata for a :class:`Component`. It contains
    the binary data itself. Every time a ``Component``'s data is updated, a new
    ``ComponentRevision`` is created.

    .. warning :: The implementation of this class is incomplete and may change
                  in the future.

    """
    data = models.BinaryField(null=True, blank=True)
    metadata = JSONField(default=None, null=True, blank=True)
    version = models.IntegerField(null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    component = models.ForeignKey('Component', related_name='revisions')

    def __str__(self):
        return "{} v{}".format(self.component.slug, self.version)
