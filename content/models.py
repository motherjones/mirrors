from django.dispatch import receiver
from django.db import models

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

class ContentAttribute(models.Model):
    """Named attributes that associate :py:class:`Content` objects with
    other `Content` objects.
    """
    parent = models.ForeignKey('Content', related_name='attributes')
    child = models.ForeignKey('Content')
    name = models.CharField(max_length=255)

class ContentMembers(models.Model):
    """Ordered list of :py:class:`Content` objects that belong to another
    `Content` object.
    """
    parent = models.ForeignKey('Content', related_name='members')
    child = models.ForeignKey('Content')
    order = models.IntegerField(default=0)

class ContentRevision(models.Model):
    """A revision of the data contained by a :class: Content object.

    .. todo:: Write real documentation for content.ContentRevision
    """
    data = models.BinaryField()
    diff = models.BinaryField(null=True, blank=True)
    metadata = JSONField()

    revision_date = models.DateTimeField(auto_now_add=True)
    revision_number = models.IntegerField(default=1)

    content = models.ForeignKey('Content', related_name='revisions')
