import json
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status

from mirrors.models import *
from mirrors.serializers import ComponentSerializer

LOGGER = logging.getLogger(__name__)


class ComponentList(mixins.CreateModelMixin,
                    generics.GenericAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ComponentDetail(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    """
    View for a single Component instance.
    """
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        data = request.DATA
        if 'metadata' in data and isinstance(data['metadata'], str):
            data['metadata'] = json.loads(data['metadata'])

        component = get_object_or_404(Component, slug=kwargs['slug'])
        serializer = self.get_serializer(instance=component,
                                         data=data,
                                         partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
