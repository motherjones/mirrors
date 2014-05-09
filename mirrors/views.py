import json
import logging

# TODO: these will have to be used at some point, but not yet
# from django.core.files.storage import default_storage
# from django.core.files import File
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import View

from rest_framework import generics, mixins, status
from rest_framework.response import Response

from mirrors.models import Component
from mirrors.serializers import ComponentSerializer
from mirrors import components

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

    def handle_uploaded_file(self, f):
        data = b''
        for chunk in f.chunks():
            # destination.write(chunk)
            data = data + chunk

        LOGGER.info("received file {} ({} bytes)".format(f.name,
                                                         f.size))

        return data

    def post(self, request, *args, **kwargs):
        component = get_object_or_404(Component, slug=kwargs['slug'])

        if len(request.FILES) != 1:
            error = {'File': ['Exactly one file per upload allowed']}
            return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)

        filedata = self.handle_uploaded_file(request.FILES['file'])
        component.new_revision(data=filedata)

        return HttpResponse({'received': len(filedata)},
                            content_type='application/json',
                            status=status.HTTP_201_CREATED)


def component_schemas(request):
    schemas = components.get_components()
    for key, schema in schemas.items():
        schemas[key] = schema
    schemas['id'] = reverse('component-schemas')
    return HttpResponse(json.dumps(schemas, indent=4),
                        content_type="application/json")
