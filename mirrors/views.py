import logging

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mirrors.models import *
from mirrors.serializers import ComponentSerializer

LOGGER = logging.Logger(__name__)


class ComponentDetail(APIView):
    """
    View for a single Component instance.
    """
    def get_object(self, slug):
        try:
            return Component.objects.get(slug=slug)
        except Component.DoesNotExist:
            LOGGER.debug("unable to fetch component {}".format(slug))
            raise Http404

    def get(self, request, slug):
        component = self.get_object(slug)
        serializer = ComponentSerializer(component)
        return Response(serializer.data)


def component_data_uri(request, slug):    
    asset = get_object_or_404(Component, slug=slug)
    response = HttpResponse(asset.binary_data, mimetype=asset.content_type)
    response['Content-Disposition'] = 'inline; filename=%s'%slug
    return response
