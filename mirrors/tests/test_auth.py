from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class ComponentAuthenticationTest(APITestCase):
    fixtures = ['users.json', 'component_data.json']

    def test_noauthed_rejects(self):
        url = reverse('component-detail', kwargs={
            'slug': 'component-with-svg-data',
            'year': 2014,
            'month': 5
        })

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_authed_as_user_accepts(self):
        url = reverse('component-detail', kwargs={
            'slug': 'component-with-svg-data',
            'year': 2014,
            'month': 5
        })

        self.client.login(username='test_user', password='password1')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_authed_as_staff_accepts(self):
        url = reverse('component-detail', kwargs={
            'slug': 'component-with-svg-data',
            'year': 2014,
            'month': 5
        })

        self.client.login(username='test_staff', password='password1')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_authed_as_admin_accepts(self):
        url = reverse('component-detail', kwargs={
            'slug': 'component-with-svg-data',
            'year': 2014,
            'month': 5
        })

        self.client.login(username='test_admin', password='password1')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
