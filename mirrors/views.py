import json
import logging

import jsonschema

# TODO: these will have to be used at some point, but not yet
# from django.core.files.storage import default_storage
# from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import transaction
# from django.db.utils import IntegrityError
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import View

from rest_framework import generics, mixins, status, permissions
from rest_framework.authentication import SessionAuthentication
# from rest_framework.views import APIView
from rest_framework.response import Response

from mirrors.components import get_component, MissingComponentException
from mirrors.models import Component, ComponentAttribute
from mirrors.serializers import ComponentSerializer
from mirrors.serializers import ComponentAttributeSerializer
from mirrors.serializers import ComponentRevisionSerializer
from mirrors import components

LOGGER = logging.getLogger(__name__)


class ComponentList(mixins.CreateModelMixin,
                    generics.GenericAPIView):
    """Handle the POST requests made to ``/component`` to allow the creation of
    new Components.
    """
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ComponentDetail(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    """View for a single Component instance."""
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ComponentAttributeList(mixins.CreateModelMixin,
                             generics.GenericAPIView):

    queryset = ComponentAttribute.objects.all()
    serializer_class = ComponentAttributeSerializer

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

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

    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

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

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().count() == 0:
            raise Http404

        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ComponentRevisionList(mixins.RetrieveModelMixin,
                            generics.GenericAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        component = get_object_or_404(Component, slug=kwargs['slug'])
        qs = component.revisions.order_by('version')

        if qs.count() == 0:
            raise Http404

        serializer = ComponentRevisionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComponentRevisionDetail(mixins.RetrieveModelMixin,
                              generics.GenericAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        component = get_object_or_404(Component, slug=kwargs['slug'])
        version = int(kwargs['version'])

        if not component._version_in_range(version):
            raise Http404()

        serializer = ComponentSerializer(component, version=version)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComponentRevisionData(mixins.RetrieveModelMixin,
                            generics.GenericAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        component = get_object_or_404(Component, slug=kwargs['slug'])
        version = int(kwargs['version'])
        data = component.binary_data_at_version(version)

        if data is None:
            raise Http404

        if 'filename' in component.metadata:
            filename = component.metadata['filename']
        else:
            filename = component.slug

        resp = HttpResponse(data,
                            content_type=component.content_type,
                            status=status.HTTP_200_OK)
        resp['Content-Disposition'] = "inline; filename={}".format(filename)
        return resp


class ComponentData(View):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        component = get_object_or_404(Component, slug=kwargs['slug'])
        data = component.binary_data

        if data is None:
            raise Http404

        # if we have a real filename stored in metadata, we should provide that
        # to the browser as the filename. if not, just give it the slug instead
        metadata = component.metadata

        if metadata is not None and 'filename' in metadata:
            filename = metadata['filename']
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


class ComponentValidity(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        component_slug = kwargs['slug']
        component = get_object_or_404(Component, slug=component_slug)

        try:
            schema = get_component(component.schema_name)
        except MissingComponentException as exc:
            response_dict = {
                'valid': False
            }

            LOGGER.error(
                "User attempted to use invalid schema name {}".format(
                    component.schema_name
                ),
                exc
            )
            return HttpResponse(json.dumps(response_dict),
                                content_type='application/json',
                                status=status.HTTP_200_OK)
        try:
            serialized_component = ComponentSerializer(component).data
        except IndexError:
            response_dict = {
                'valid': True,
                'errors': {
                    'version': 'Unable to retrieve requested component version'
                }
            }

        # TODO: in the future we may want to go and actually inspect the data
        # to see *what* is wrong, but for now all we're interested in is
        # whether the thing is or isn't a valid Component
        schemas = {k: v() for k, v in components.get_components().items()}

        try:
            validator = jsonschema.Draft3Validator(schemas)
            validator.validate(serialized_component, schema())
            response_dict = {'valid': True}
        except jsonschema.ValidationError:
            response_dict = {'valid': False}

        return HttpResponse(json.dumps(response_dict),
                            content_type='application/json',
                            status=status.HTTP_200_OK)


def component_schemas(request):
    schemas = components.get_components()
    for key, schema in schemas.items():
        schemas[key] = schema()
    schemas['id'] = reverse('component-schemas')
    return HttpResponse(json.dumps(schemas, indent=4),
                        content_type="application/json")
