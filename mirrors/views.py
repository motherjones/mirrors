import json
import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import View

from rest_framework.views import APIView
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

        d_fixed = dict(data)

        for k in d_fixed.keys():
            if isinstance(d_fixed[k], list):
                d_fixed[k] = d_fixed[k][0]

        serializer = ComponentSerializer(component, data=d_fixed, partial=True)

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

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

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
    lookup_field = 'attr_name'
    serializer_class = ComponentAttributeSerializer

    def get_queryset(self):
        component = self.kwargs['slug']
        attr_name = self.kwargs.get('attr_name', None)

        parent = get_object_or_404(Component, slug=component)
        queryset = parent.attributes

        if attr_name is not None:
            queryset = queryset.filter(name=self.kwargs['attr_name'])
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

    def post(self, request, *args, **kwargs):
        request.DATA['parent'] = kwargs['slug']
        request.DATA['name'] = kwargs['attr_name']

        serializer = ComponentAttributeSerializer(data=request.DATA,
                                                  partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        request.DATA['parent'] = kwargs['slug']
        request.DATA['name'] = kwargs['attr_name']

        if queryset.count() == 1:
            serializer = ComponentAttributeSerializer(data=request.DATA,
                                                      partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            # TODO: not this
            raise Http404

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


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
