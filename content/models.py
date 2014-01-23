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
    schema = JSONField()
    parent_content = models.ForeignKey(
        'self',
        related_name='children',
        blank=True,
        null=True,
        default=None
    )

    @property
    def binary_data(self):
        """Get the data from the most recent revision of the data.
        
        :rtype: bytes
        """
        rev = self.revisions.order_by('revision').first()
        data = None

        if rev:
            data = rev.data.tobytes()

        return data


class ContentRevision(models.Model):
    """A revision of the data contained by a :class: Content object.

    .. todo:: Write real documentation for content.ContentRevision
    """
    data = models.BinaryField()
    diff = models.BinaryField()
    revision_date = models.DateTimeField(auto_now_add=True)
    revision_number = models.IntegerField()

    content = models.ForeignKey('Content', related_name='revisions')
