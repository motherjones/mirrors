from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mirrors.models import Content, ContentMembers, ContentAttribute
from mirrors.models import ContentRevision
from mirrors.serializers import ContentSerializer


def get_content(request, slug):
    raise NotImplementedError


def get_content_data(request, slug):
    raise NotImplementedError


def get_content_revision(request, slug, revision):
    raise NotImplementedError


def get_content_revision_data(request, slug, revision):
    raise NotImplementedError
