from django.dispatch import receiver
from django.db import models

from jsonfield import JSONField


class Content(models.Model):
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
        """Get the data from the most recent revision and return it as a
        bytes object.
        """
        rev = self.revisions.order_by('-revision_date').first()
        data = None

        if rev:
            data = rev.data.tobytes()

        return data


class ContentRevision(models.Model):
    data = models.BinaryField()
    diff = models.BinaryField()
    revision_date = models.DateTimeField(auto_now_add=True)

    content = models.ForeignKey('Content', related_name='revisions')
