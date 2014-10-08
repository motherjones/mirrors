from django.test import TestCase
from mirrors_publisher.models import PublishedRevision
from mirrors.models import Component


class PublisherJobTest(TestCase):
    fixtures = ['components.json']

    def setUp(self):
        self.component1 = Component.objects.get(pk=14)

    def test_creation(self):
        job = PublisherJob.objects.create(self.component1)
        self.assertEqual(job.components, [component])

    # All the cases we want to test:
    # Single component, no parents or children
    # Single component with multiple revisions, publish current
    # Single component with multiple revisions, publish specific rev
    # Component w/ child
    # Component w/ parent and child
    # Selectively publishing component (ie, component has changes but children
    #   have not changed)
    # Array of components ??

    def test_single_component(self):
        # If revision field is NULL, then the object will always refer to the most recent revision for that Component.
        pubrev = PublisherJob.objects.create(initial_component=self.component2)
        self.assertEqual(job.state, PublisherJob.SUCCESS)
