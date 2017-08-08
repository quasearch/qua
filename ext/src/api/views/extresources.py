import logging

from django.conf import settings
from rest_framework.views import APIView

from api import serializers
from api.models import ExternalResource
from api.pagination import paginate
from api.serializers import serialize, deserialize
from app.response import QuaApiResponse


log = logging.getLogger(settings.APP_NAME + __name__)


class ExtResources(APIView):

    @paginate
    def get(self, request, limit=settings.PAGE_SIZE, offset=0):
        '''Get list of external resources'''

        extresources = ExternalResource.get(limit=limit, offset=offset)
        serializer = serialize(serializers.ExtResourceList, extresources)

        return QuaApiResponse(serializer.data)

    def post(self, request):
        '''Create new external resource'''

        serializer = deserialize(serializers.ExtResource, data=request.data)
        serializer.save(user=request.user)

        return QuaApiResponse(serializer.data)


class ExtResource(APIView):

    def get(self, request, extresource_id):
        '''Get extresource by extresource_id'''

        extresource = ExternalResource.get(pk=extresource_id)
        serializer = serialize(serializers.ExtResource, extresource)

        return QuaApiResponse(serializer.data)

    def delete(self, request, extresource_id):
        '''Delete specific external resource'''

        extresource = ExternalResource.get(pk=extresource_id)
        extresource.delete()

        return QuaApiResponse()
