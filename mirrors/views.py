from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mirrors.models import *
from mirrors.serializers import ComponentSerializer


def get_component(request, slug):
    raise NotImplementedError


def get_component_data(request, slug):
    raise NotImplementedError


def get_component_revision(request, slug, revision):
    raise NotImplementedError


def get_component_revision_data(request, slug, revision):
    raise NotImplementedError
