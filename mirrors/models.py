import re
import sys 

from django.dispatch import receiver
from django.db import models
from django.db.models import Max
from django.utils import timezone

from jsonfield import JSONField


class Content(models.Model):
    """A piece of content.

    .. todo:: Write real documentation for content.Content
    """
    slug = models.SlugField(max_length=100, unique=True)
    metadata = JSONField()
    content_type = models.CharField(max_length=50, default='none')
    publish_date = models.DateTimeField(null=True)
    schema_name = models.CharField(max_length=50, null=True, blank=True)

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
        """Create a new revision for this :py:class:`Content` object. If the
        data is not in the correct format it will attempt to convert it into a
        bytes object.

        Passing None for one of the arguments will result in that data not
        being changed.

        :param data: the actual content of the new revision
        :type data: `bytes`
        :param metadata: the new metadata
        :type metadata: `dict`

        :rtype: :py:class:`ContentRevision`
        :raises: `ValueError`
        """
        if not data and not metadata:
            raise ValueError('no new data was actually provided')

        cur_rev_num = self.revisions.aggregate(
            Max('revision_number')
        )['revision_number__max']

        try:
            cur_rev = self.revisions.get(revision_number=cur_rev_num)

            new_data = cur_rev.data
            new_metadata = cur_rev.metadata
        except ContentRevision.DoesNotExist:
            cur_rev_num = 0
            new_data = None
            new_metadata = self.metadata

            if not data:
                raise ValueError(
                    'both metadata and data must be provided for 1st revision'
                )

        if data:
            new_data = data
        if metadata:
            new_metadata = metadata

        new_rev = ContentRevision.objects.create(
            revision_number=cur_rev_num+1,
            data=data,
            diff=None,  # figure this out later
            metadata=metadata,
            revision_date=timezone.now(),
            content=self
        )

        return new_rev

    def new_attribute(self, name, child):
        """Add a new named attribute to the :py:class:`Content` object. This
        will overwrite any old attributes that may have already existed.

        :param name: the attribute's name, which can only contain alphanumeric
                     characters as well as the - and _ characters.
        :type name: string
        :param child: the `Content` object to associate with that name
        :type child: `Content`

        :rtype: :py:class:`ContentAttribute`
        """
        if not child or child == self:
            raise ValueError('child cannot be None or self')

        if not re.match('[a-zA-Z0-9_-]+', name):
            raise KeyError('invalid attribute name')

        attribute = ContentAttribute()

        try:
            self.attributes.get(parent=self, name=name).delete()
        except ContentAttribute.DoesNotExist:
            pass

        return ContentAttribute.objects.create(
            name=name,
            parent=self,
            child=child
        )

    def get_attribute(self, attribute_name):
        """Retrieve the `Content` object attached to this one by the
        attribute name.

        :param attribute_name: name of the attribute 
        :type attribute_name: str
        :rtype: `Content`
        """
        try:
            attr = ContentAttribute.objects.get(parent=self,
                                                name=attribute_name)
            return attr.child
        except ContentAttribute.DoesNotExist:
            raise KeyError("no such attribute '{}'".format(attribute_name))

    def new_member(self, child, index=None):
        """Add an existing `Content` object entry to the ordered list of
        members for this one. By default, this will simply append the child
        object to the list, but the user can specify the order if they so
        wish.

        Elements inserted into the list at index `n` will shift all elements
        back by one.

        :param child: the child `Content` object
        :type child: `Content`
        :param index: (optional) the position within the list to put the child
                      in
        :type index: integer
        """
        count = self.members.count()

        if index == None:
            new_index = count
        else:
            new_index = index

        indices = []

        l_el_ord = 0
        r_el_ord = ContentMember.max_index

        if new_index < 0 or new_index > count:
            raise IndexError('index provided is out of bounds')

        if new_index == count:
            if count > 0:
                l_el_ord = self.members.order_by('order').last().order
        else:
            if new_index == 0:
                r_el_ord = self.members.order_by('order').first().order
            else:
                indices = [ m.order for m in self.members.order_by('order')]

                l_el_ord = indices[new_index-1]
                r_el_ord = indices[new_index]

        new_order = (l_el_ord + r_el_ord) / 2

        return ContentMember.objects.create(
            parent=self,
            child=child,
            order=new_order
        )

    def get_member(self, index):
        """Retrieve a specific member.

        :param index: the index of the member
        :type index: int
        :rtype: :py:class:`Content`
        """
        # TODO implement Content.get_member
        if index < 0 or index > self.members.count():
            raise IndexError('member index out of bounds')

        member = self.members.order_by('order')[index:index+1].first()
        return member.child


class ContentAttribute(models.Model):
    """Named attributes that associate :py:class:`Content` objects with
    other `Content` objects.
    """
    parent = models.ForeignKey('Content', related_name='attributes')
    child = models.ForeignKey('Content')
    name = models.CharField(max_length=255)

    added_time = models.DateTimeField(auto_now_add=True)


class ContentMember(models.Model):
    """Ordered list of :py:class:`Content` objects that belong to another
    `Content` object.
    """
    max_index = 1000000000

    parent = models.ForeignKey('Content', related_name='members')
    child = models.ForeignKey('Content')
    order = models.IntegerField(default=0)


class ContentRevision(models.Model):
    """A revision of the data contained by a :py:class:Content object.

    .. todo:: Write real documentation for content.ContentRevision
    """
    data = models.BinaryField()
    diff = models.BinaryField(null=True, blank=True)
    metadata = JSONField()

    revision_date = models.DateTimeField(auto_now_add=True)
    revision_number = models.IntegerField(default=1)

    content = models.ForeignKey('Content', related_name='revisions')
