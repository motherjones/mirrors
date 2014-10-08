from django.db import models


class PublisherJob(models.Model):
    SUCCESS = 1
    FAILURE = 2
    INCOMPLETE = 3
    STATE_CHOICES = (
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (INCOMPLETE, 'Incomplete'),
    )
    date = models.DateTimeField()
    # components = models.ManyToManyField("self")
    affected_components = models.ManyToManyField('mirrors.models.Component', through='PublishedRevision')
    state = models.IntegerField(choices=STATE_CHOICES, default=0)

    @property
    def component_list(self):
        return list(self.components.all())

    def __init__(self, intial_components):
        components = initial_components

    def publish(self):
        # Find parents & children of each component
        # Separate static components from dynamic components
        # For each type
        #   get revision to publish
        #   create 'PublishedRevision' reciept for each
        #   publish with backend specified or then use default.
        # Need to check and diminish race conditions.
        return False


class PublishedRevision(models.Model):
    SUCCESS = 1
    FAILURE = 2
    SKIPPED = 3
    STATE_CHOICES = (
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (SKIPPED, 'Skipped'),
    )

    job = models.ForeignKey(PublisherJob)
    component = models.ForeignKey('mirrors.models.Component')
    revision = models.ForeignKey('mirrors.models.ComponentRevision',
                                 null=True,
                                 blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    state = models.IntegerField(choices=STATE_CHOICES, default=0)

