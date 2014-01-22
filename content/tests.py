import json

from django.test import TestCase
from content.models import Content, ContentRevision


class ContentTests(TestCase):
    fixtures = ['content.json']

    def test_get_binary_data(self):
        c = Content.objects.get(slug='test-content-1')
        self.assertEqual(c.binary_data, b'this is the second revision')

    def test_get_binary_data_failure(self):
        c = Content.objects.get(slug='content-with-no-revisions')
        self.assertEqual(c.binary_data, None)
