import datetime
import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils.timezone import utc
from django.core.urlresolvers import reverse

from jsonfield import JSONField

from mirrors.exceptions import LockEnforcementError


def validate_is_year(value):
    """Validate that the given value is a year (ie >= 0).
    :param value: the value to validate
    :type value: int

    :raises: :class:`ValidationError`
    """

    if value < 0:
        raise ValidationError('Not a valid year value')


def validate_is_month(value):
    """Validate that the given value is a month (ie 1 <= value <= 12)

    :param value: the value to validate
    :type value: int

    :raises: :class:`ValidationError`
    """
    if value < 1 or value > 12:
        raise ValidationError('Not a valid month value')


class Component(models.Model):
    """A ``Component`` is the basic type of object for all things in the Mirrors
    content repository. Anything that has a presence in the final output of the
    website is made of at least one ``Component`` object, and will generally be
    made from several few.

    .. note :: ``Component`` objects all have a year and associated with them
               so that they can be presented in
               ``/component/<YYYY>/<MM>/<slug>`` format. If the value of both
               of those are 0, they are treated as having no associated year
               and month and are presented in ``/component/<slug>`` format.
    

    .. warning :: The implementation of this class is incomplete and may change
                  in the future.

    """
    slug = models.SlugField(max_length=100, null=False, blank=False)
    year = models.IntegerField(default=0,
                               null=False,
                               blank=False,
                               validators=[validate_is_year])
    month = models.IntegerField(default=0,
                                null=False,
                                blank=False,
                                validators=[validate_is_month])

    content_type = models.CharField(max_length=50, default='none')
    schema_name = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('slug', 'year', 'month'),)
        index_together = ['slug', 'year', 'month']

    def clean(self):
        if bool(self.year != 0) != bool(self.month != 0):
            # logical xor
            raise ValidationError(
                'Either both year and month must be defined, or neither')

    @property
    def data_uri(self):
        """Get the URI for this ``Component``.

        :rtype: str
        """
        if self.binary_data is not None:
            return reverse('component-data', kwargs={'slug': self.slug,
                                                     'year': self.year,
                                                     'month': self.month})
        else:
            return None

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

        # attr never gets used again... just comented this out for now
        # if self.attributes.filter(name=name).count() == 1:
        #     attr = self.attributes.get(name=name)

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
            return {}

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
            return bytes(rev.data)
        else:
            return None

    @property
    def lock(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)

        cur_lock = self.locks.exclude(broken=True)
        cur_lock = cur_lock.exclude(lock_ends_at__lte=now)

        if cur_lock.count() > 0:
            return cur_lock.first()
        else:
            return None

    def lock_by(self, user, lock_period=60):
        """Lock the :class:`Component`, preventing other users from altering it
        until the lock expires.

        :param value: The user that has requested the lock be created.
        :type User: :class:`User`

        :rtype: :class:`ComponentLock`
        """
        if self.lock is not None:
            raise LockEnforcementError(locking_user=self.lock.locked_by,
                                       ends_at=self.lock.lock_ends_at)

        lock = ComponentLock()
        t_delta = datetime.timedelta(minutes=lock_period)
        now = datetime.datetime.utcnow().replace(tzinfo=utc)

        lock.component = self
        lock.locked_by = user
        lock.lock_ends_at = now + t_delta
        lock.save()

        return lock

    def unlock(self, unlocking_user):
        """Unlock the :class:`Component`.

        :param unlocking_user: The user that has requested the lock be broken.
        :type unlocking_user: :class:`User`
        """
        # TODO: right now we don't care who breaks a lock, but eventually
        # authorization will have to be implemented

        # we have to assign self.lock to a new variable because if we don't,
        # because otherwise it'll keep executing SQL queries
        lock = self.lock

        if lock is not None:
            lock.broken = True
            lock.save()

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


class ComponentLock(models.Model):
    """ Determines whether a ``Component`` can be edited.
    """
    locked_by = models.ForeignKey(User)
    locked_at = models.DateTimeField(auto_now_add=True)
    lock_ends_at = models.DateTimeField()
    component = models.ForeignKey('Component', related_name='locks')

    broken = models.BooleanField(default=False)

    def extend_lock(self, *args, **kwargs):
        """Extend the life time of the current lock. The arguments excepted are the
        same as what is acceptable for use when creating a
        :class:`datetime.timedelta` object.

        :raises: :class:`ValueError`
        """
        delta = datetime.timedelta(**kwargs)
        if delta.total_seconds() < 0:
            raise ValueError()

        self.lock_ends_at = self.lock_ends_at + delta
        self.save()

    def __str__(self):
        return "{} locked by {} until {}".format(self.component.slug,
                                                 self.locked_by.username,
                                                 self.lock_ends_at)
