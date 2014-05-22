import json
import logging

from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import View

from rest_framework.response import Response
from rest_framework import generics, mixins, status

from mirrors.models import Component, ComponentAttribute
from mirrors.serializers import ComponentSerializer
from mirrors.serializers import ComponentAttributeSerializer

from mirrors import components

LOGGER = logging.getLogger(__name__)


class ComponentList(mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """Handle the POST requests made to ``/component`` to allow the creation of
    new Components.
    """
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ComponentDetail(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    """View for a single Component instance."""
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        data = request.DATA
        component = get_object_or_404(Component, slug=kwargs['slug'])
        serializer = ComponentSerializer(component)

        if 'metadata' in data:
            new_metadata = {}
            patch_metadata = data['metadata']
            old_metadata = serializer.data['metadata']

            for k in old_metadata.keys():
                new_metadata[k] = patch_metadata.get(k, old_metadata[k])

            data['metadata'] = new_metadata

        serializer = ComponentSerializer(component,
                                         data=dict(data),
                                         partial=True)

        if serializer.is_valid():
            serializer.save()
            LOGGER.debug("saved changes to {}: {}".format(kwargs['slug'],
                                                          data))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            LOGGER.debug(
                "error saving changes to {}: {}".format(kwargs['slug'],
                                                        serializer.errors))
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ComponentAttributeList(mixins.CreateModelMixin,
                             generics.GenericAPIView):

    queryset = ComponentAttribute.objects.all()
    serializer_class = ComponentAttributeSerializer

    def post(self, request, *args, **kwargs):
        parent = Component.objects.get(slug=kwargs['slug'])
        attrs = parent.attributes.filter(name=request.DATA['name'])

        if attrs.count() > 0:
            return Response(data='Attribute name is already taken',
                            status=status.HTTP_409_CONFLICT)
        request.DATA['parent'] = kwargs['slug']
        del kwargs['slug']

        if 'slug' in request.DATA:
            del request.DATA['slug']

        return self.create(request, *args, **kwargs)


class ComponentAttributeDetail(mixins.UpdateModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               generics.GenericAPIView):
    queryset = ComponentAttribute.objects.all()
    lookup_field = 'name'
    serializer_class = ComponentAttributeSerializer

    def _normalize_request_data(self, data):
        """Turn a single or list of client-submitted component attributes into
        something that the serializer understands by setting the value of
        `attribute['parent']` to the component slug and `attribute['name']` to
        the attribute name.

        :param data: The data to normalize; generally requset.DATA
        :type data: `list` or `dict`
        :raise TypeError: If data is not a list or or dict
        :return: the normalized data
        """
        if isinstance(data, list):
            new_data = []
            for attr in data:
                attr['parent'] = self.kwargs['slug']
                attr['name'] = self.kwargs['name']
                new_data.append(attr)
            return new_data
        elif isinstance(data, dict):
            data['parent'] = self.kwargs['slug']
            data['name'] = self.kwargs['name']
            return data
        else:
            raise TypeError('ComponentAttribute data must be a list or a dict')

    def get_queryset(self):
        component = self.kwargs['slug']
        attr_name = self.kwargs.get('name', None)

        parent = get_object_or_404(Component, slug=component)
        queryset = parent.attributes

        if attr_name is not None:
            queryset = queryset.filter(name=self.kwargs['name'])
            queryset = queryset.order_by('weight')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.count() == 0:
            raise Http404
        elif queryset.count() == 1:
            serializer = ComponentAttributeSerializer(queryset.first())
        else:
            serializer = ComponentAttributeSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        try:
            data = self._normalize_request_data(request.DATA)
        except TypeError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        has_many = isinstance(data, list)
        serializer = ComponentAttributeSerializer(data=data, many=has_many)

        if serializer.is_valid():
            with transaction.atomic():
                qs = self.get_queryset()
                if qs.count() > 0:
                    qs.delete()
                serializer.save()

            if has_many:
                serializer = ComponentAttributeSerializer(self.get_queryset(),
                                                          many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        request.DATA['parent'] = kwargs['slug']
        request.DATA['name'] = kwargs['name']

        if queryset.count() != 1:
            raise Http404

        serializer = ComponentAttributeSerializer(data=request.DATA,
                                                  partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().count() == 0:
            raise Http404

        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ComponentData(View):
    def get(self, request, *args, **kwargs):
        component = get_object_or_404(Component, slug=kwargs['slug'])
        data = component.binary_data

        if data is None:
            raise Http404

        # if we have a real filename stored in metadata, we should provide that
        # to the browser as the filename. if not, just give it the slug instead
        if 'filename' in component.metadata:
            filename = component.metadata['filename']
        else:
            filename = component.slug

        resp = HttpResponse(data,
                            content_type=component.content_type,
                            status=status.HTTP_200_OK)
        resp['Content-Disposition'] = "inline; filename={}".format(filename)
        return resp

    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


def component_schemas(request):
    schemas = components.get_components()
    for key, schema in schemas.items():
        schemas[key] = schema
    schemas['id'] = reverse('component-schemas')
    return HttpResponse(json.dumps(schemas, indent=4),
                        content_type="application/json")
